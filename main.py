# main.py - Eco Eletrônico COMPLETO
# Com: FIRESTORE + AUTENTICAÇÃO + IMPACTO AMBIENTAL + LGPD + BIG DATA
# Sugestões implementadas do ChatGPT
# Requisitos: pip install streamlit firebase-admin bcrypt
# Rode: streamlit run main.py

import streamlit as st
from datetime import datetime
import random
import json
import re
import bcrypt
import firebase_admin
from firebase_admin import credentials, firestore

# Importar base de dados de impacto ambiental
try:
    from database_impacto import calcular_impacto_total, formatar_impacto_ambiental, IMPACTO_AMBIENTAL
    IMPACTO_DISPONIVEL = True
except ImportError:
    IMPACTO_DISPONIVEL = False
    def calcular_impacto_total(m, q): return None
    def formatar_impacto_ambiental(i): return ""

# ========================================
# CONFIGURAÇÃO DO FIRESTORE
# ========================================

@st.cache_resource
def init_firestore():
    """Inicializa Firestore (funciona local E no Streamlit Cloud)"""
    if not firebase_admin._apps:
        try:
            # MODO 1: Streamlit Cloud (usando secrets)
            if "firebase" in st.secrets:
                # OPÇÃO A: JSON completo como string
                if isinstance(st.secrets["firebase"]["key"], str):
                    key_dict = json.loads(st.secrets["firebase"]["key"])
                # OPÇÃO B: Campos separados
                else:
                    key_dict = dict(st.secrets["firebase"]["key"])
                
                cred = credentials.Certificate(key_dict)
            
            # MODO 2: Local (usando arquivo)
            else:
                cred = credentials.Certificate('firebase-credentials.json')
            
            firebase_admin.initialize_app(cred)
            return firestore.client()
        
        except Exception as e:
            st.error(f"❌ Erro Firestore: {e}")
            return None
    return firestore.client()

db = init_firestore()

# ========================================
# FUNÇÕES DE VALIDAÇÃO E SEGURANÇA
# ========================================

def validar_email(email):
    """Valida formato de e-mail"""
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(padrao, email) is not None

def validar_senha(senha):
    """Valida força da senha (mínimo 6 caracteres)"""
    if len(senha) < 6:
        return False, "A senha deve ter no mínimo 6 caracteres"
    return True, "Senha válida"

def hash_senha(senha):
    """Cria hash seguro da senha"""
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verificar_senha(senha, hash_armazenado):
    """Verifica se a senha corresponde ao hash"""
    return bcrypt.checkpw(senha.encode('utf-8'), hash_armazenado.encode('utf-8'))

# ========================================
# FUNÇÕES DE AUTENTICAÇÃO
# ========================================

def email_existe(email):
    """Verifica se e-mail já está cadastrado"""
    if not db:
        return False
    
    usuarios_ref = db.collection('usuarios')
    query = usuarios_ref.where('email', '==', email.lower()).limit(1)
    results = list(query.stream())
    
    return len(results) > 0

def criar_usuario(nome, turma, email, senha):
    """Cria novo usuário com autenticação"""
    if not db:
        return None, "Erro: Firestore não conectado"
    
    # Validações
    if not nome.strip():
        return None, "Nome é obrigatório"
    
    if not validar_email(email):
        return None, "E-mail inválido"
    
    valido, msg = validar_senha(senha)
    if not valido:
        return None, msg
    
    if email_existe(email):
        return None, "E-mail já cadastrado"
    
    # Criar usuário
    user_id = int(datetime.now().timestamp() * 1000)
    senha_hash = hash_senha(senha)
    
    dados = {
        'id': user_id,
        'nome': nome.strip(),
        'turma': turma,
        'email': email.lower().strip(),
        'senha': senha_hash,
        'pontos': 0.0,
        'categoriasCompradas': {
            '1': [],  # Trimestre 1
            '2': [],  # Trimestre 2
            '3': []   # Trimestre 3
        },
        'dataCadastro': datetime.now(),
        'ativo': True
    }
    
    # Salva no Firestore
    db.collection('usuarios').document(str(user_id)).set(dados)
    
    # Remove senha do retorno por segurança
    dados_retorno = dados.copy()
    del dados_retorno['senha']
    
    return dados_retorno, "Usuário criado com sucesso"

def buscar_usuario(email, senha):
    """Autentica usuário com e-mail e senha"""
    if not db:
        return None
    
    if not validar_email(email):
        return None
    
    # Buscar usuário por e-mail
    usuarios_ref = db.collection('usuarios')
    query = usuarios_ref.where('email', '==', email.lower()).limit(1)
    results = list(query.stream())
    
    if not results:
        return None
    
    user_data = results[0].to_dict()
    
    # Verificar se usuário está ativo
    if not user_data.get('ativo', True):
        return None
    
    # Verificar senha
    if not verificar_senha(senha, user_data['senha']):
        return None
    
    # Converter Timestamp para string
    if 'dataCadastro' in user_data and hasattr(user_data['dataCadastro'], 'strftime'):
        user_data['dataCadastro'] = user_data['dataCadastro'].strftime('%d/%m/%Y %H:%M')
    
    # Garantir estrutura de trimestres
    if 'categoriasCompradas' not in user_data or not isinstance(user_data['categoriasCompradas'], dict):
        user_data['categoriasCompradas'] = {'1': [], '2': [], '3': []}
    
    # Remove senha do retorno por segurança
    if 'senha' in user_data:
        del user_data['senha']
    
    return user_data

def alterar_senha(user_id, senha_atual, senha_nova):
    """Altera senha do usuário"""
    if not db:
        return False, "Erro: Firestore não conectado"
    
    # Buscar usuário
    user_ref = db.collection('usuarios').document(str(user_id))
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        return False, "Usuário não encontrado"
    
    user_data = user_doc.to_dict()
    
    # Verificar senha atual
    if not verificar_senha(senha_atual, user_data['senha']):
        return False, "Senha atual incorreta"
    
    # Validar nova senha
    valido, msg = validar_senha(senha_nova)
    if not valido:
        return False, msg
    
    # Atualizar senha
    novo_hash = hash_senha(senha_nova)
    user_ref.update({'senha': novo_hash})
    
    return True, "Senha alterada com sucesso"

def recuperar_senha(email):
    """Gera código de recuperação de senha"""
    if not db:
        return None, "Erro: Firestore não conectado"
    
    if not validar_email(email):
        return None, "E-mail inválido"
    
    # Verificar se e-mail existe
    usuarios_ref = db.collection('usuarios')
    query = usuarios_ref.where('email', '==', email.lower()).limit(1)
    results = list(query.stream())
    
    if not results:
        return None, "E-mail não encontrado"
    
    # Gerar código de recuperação
    codigo = f"{random.randint(100000, 999999)}"
    
    # Salvar código temporário (válido por 15 minutos)
    user_doc = results[0]
    user_doc.reference.update({
        'codigoRecuperacao': codigo,
        'codigoExpiracao': datetime.now().timestamp() + 900  # 15 minutos
    })
    
    return codigo, f"Código de recuperação gerado (em produção seria enviado por e-mail)"

def resetar_senha_com_codigo(email, codigo, senha_nova):
    """Reseta senha usando código de recuperação"""
    if not db:
        return False, "Erro: Firestore não conectado"
    
    # Buscar usuário
    usuarios_ref = db.collection('usuarios')
    query = usuarios_ref.where('email', '==', email.lower()).limit(1)
    results = list(query.stream())
    
    if not results:
        return False, "E-mail não encontrado"
    
    user_data = results[0].to_dict()
    user_ref = results[0].reference
    
    # Verificar código
    if 'codigoRecuperacao' not in user_data:
        return False, "Nenhum código de recuperação solicitado"
    
    if user_data['codigoRecuperacao'] != codigo:
        return False, "Código incorreto"
    
    # Verificar expiração
    if datetime.now().timestamp() > user_data.get('codigoExpiracao', 0):
        return False, "Código expirado. Solicite um novo código"
    
    # Validar nova senha
    valido, msg = validar_senha(senha_nova)
    if not valido:
        return False, msg
    
    # Atualizar senha e remover código
    novo_hash = hash_senha(senha_nova)
    user_ref.update({
        'senha': novo_hash,
        'codigoRecuperacao': firestore.DELETE_FIELD,
        'codigoExpiracao': firestore.DELETE_FIELD
    })
    
    return True, "Senha resetada com sucesso"

# ========================================
# FUNÇÕES DE CONSENTIMENTO LGPD E BIG DATA
# ========================================

def verificar_consentimento(user_id):
    """Verifica se usuário já deu consentimento LGPD"""
    if not db:
        return None
    
    user_ref = db.collection('usuarios').document(str(user_id))
    user_doc = user_ref.get()
    
    if user_doc.exists:
        return user_doc.to_dict().get('consentimento_lgpd', None)
    return None

def salvar_consentimento(user_id, aceito):
    """Salva consentimento LGPD do usuário"""
    if not db:
        return False
    
    user_ref = db.collection('usuarios').document(str(user_id))
    user_ref.update({
        'consentimento_lgpd': aceito,
        'data_consentimento': datetime.now()
    })
    return True

def registrar_evento_anonimo(material, quantidade, impacto):
    """Registra evento anônimo para Big Data (se consentimento dado)"""
    if not db or not impacto:
        return
    
    evento_id = int(datetime.now().timestamp() * 1000)
    
    # Dados COMPLETAMENTE ANÔNIMOS
    dados = {
        'id': evento_id,
        'timestamp': datetime.now(),
        'categoria': impacto.get('categoria', 'N/A'),
        'material': material,
        'quantidade': quantidade,
        'metais_evitados': impacto.get('metais_pesados_total', {}),
        'co2_evitado_kg': impacto.get('co2_evitado_kg', 0),
        'energia_economizada_kwh': impacto.get('energia_economizada_kwh', 0),
        'agua_preservada_litros': impacto.get('agua_economizada_litros', 0),
        'peso_total_kg': impacto.get('peso_total_kg', 0),
        'escola': 'FECTI 2024'
    }
    
    db.collection('big_data_anonimo').document(str(evento_id)).set(dados)

def get_estatisticas_big_data():
    """Obtém estatísticas agregadas do Big Data"""
    if not db:
        return None
    
    eventos = []
    docs = db.collection('big_data_anonimo').stream()
    
    for doc in docs:
        eventos.append(doc.to_dict())
    
    if not eventos:
        return None
    
    # Calcular totais
    total = {
        'total_eventos': len(eventos),
        'total_co2_kg': sum(e.get('co2_evitado_kg', 0) for e in eventos),
        'total_energia_kwh': sum(e.get('energia_economizada_kwh', 0) for e in eventos),
        'total_agua_litros': sum(e.get('agua_preservada_litros', 0) for e in eventos),
        'total_peso_kg': sum(e.get('peso_total_kg', 0) for e in eventos),
        'total_chumbo_kg': sum(e.get('metais_evitados', {}).get('chumbo', 0) for e in eventos),
        'total_mercurio_kg': sum(e.get('metais_evitados', {}).get('mercurio', 0) for e in eventos),
        'total_cadmio_kg': sum(e.get('metais_evitados', {}).get('cadmio', 0) for e in eventos),
        'total_niquel_kg': sum(e.get('metais_evitados', {}).get('niquel', 0) for e in eventos)
    }
    
    # Contar materiais
    materiais = {}
    for e in eventos:
        mat = e.get('material', 'Desconhecido')
        materiais[mat] = materiais.get(mat, 0) + e.get('quantidade', 1)
    
    total['materiais_mais_descartados'] = sorted(materiais.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return total

# ========================================
# FUNÇÕES DE BANCO DE DADOS (FIRESTORE)
# ========================================

def buscar_usuario_por_id(user_id):
    """Busca usuário por ID"""
    if not db:
        return None
    
    user_ref = db.collection('usuarios').document(str(user_id))
    user_doc = user_ref.get()
    
    if user_doc.exists:
        data = user_doc.to_dict()
        
        # Converter Timestamp para string
        if 'dataCadastro' in data and hasattr(data['dataCadastro'], 'strftime'):
            data['dataCadastro'] = data['dataCadastro'].strftime('%d/%m/%Y %H:%M')
        
        # Garantir estrutura de trimestres
        if 'categoriasCompradas' not in data or not isinstance(data['categoriasCompradas'], dict):
            data['categoriasCompradas'] = {'1': [], '2': [], '3': []}
        
        # Remove senha por segurança
        if 'senha' in data:
            del data['senha']
        
        return data
    
    return None

def load_usuarios():
    """Carrega todos os usuários"""
    if not db:
        return []
    
    usuarios = []
    docs = db.collection('usuarios').stream()
    
    for doc in docs:
        data = doc.to_dict()
        # Converter Timestamp para string
        if 'dataCadastro' in data and hasattr(data['dataCadastro'], 'strftime'):
            data['dataCadastro'] = data['dataCadastro'].strftime('%d/%m/%Y %H:%M')
        
        # Garantir estrutura de trimestres
        if 'categoriasCompradas' not in data or not isinstance(data['categoriasCompradas'], dict):
            data['categoriasCompradas'] = {'1': [], '2': [], '3': []}
        
        # Remove senha por segurança
        if 'senha' in data:
            del data['senha']
        
        usuarios.append(data)
    
    return usuarios

def atualizar_pontos(user_id, pontos_adicionar):
    """Atualiza pontos do usuário"""
    if not db:
        return
    
    user_ref = db.collection('usuarios').document(str(user_id))
    user_doc = user_ref.get()
    
    if user_doc.exists:
        pontos_atuais = user_doc.to_dict().get('pontos', 0)
        novos_pontos = pontos_atuais + pontos_adicionar
        user_ref.update({'pontos': novos_pontos})

def adicionar_categoria_comprada(user_id, categoria, trimestre):
    """Adiciona categoria comprada no trimestre atual"""
    if not db:
        return
    
    user_ref = db.collection('usuarios').document(str(user_id))
    user_doc = user_ref.get()
    
    if user_doc.exists:
        data = user_doc.to_dict()
        categorias = data.get('categoriasCompradas', {'1': [], '2': [], '3': []})
        
        # Garantir que é um dicionário
        if not isinstance(categorias, dict):
            categorias = {'1': [], '2': [], '3': []}
        
        trimestre_str = str(trimestre)
        if trimestre_str not in categorias:
            categorias[trimestre_str] = []
        
        if categoria not in categorias[trimestre_str]:
            categorias[trimestre_str].append(categoria)
            user_ref.update({'categoriasCompradas': categorias})

def get_trimestre_atual():
    """Obtém o trimestre atual"""
    if not db:
        return 1
    
    config_ref = db.collection('config').document('sistema')
    config_doc = config_ref.get()
    
    if config_doc.exists:
        return config_doc.to_dict().get('trimestreAtual', 1)
    else:
        # Criar configuração inicial
        config_ref.set({'trimestreAtual': 1})
        return 1

def set_trimestre_atual(trimestre):
    """Define o trimestre atual"""
    if not db:
        return
    
    config_ref = db.collection('config').document('sistema')
    config_ref.set({'trimestreAtual': trimestre})

def salvar_snapshot_trimestre(trimestre, usuarios, descartes):
    """Salva snapshot do trimestre antes de resetar"""
    if not db:
        return
    
    # Criar ranking do trimestre
    ranking = []
    for user in usuarios:
        descartes_user = len([d for d in descartes if d['usuarioId'] == user['id'] and d['status'] == 'Aprovado'])
        ranking.append({
            'nome': user['nome'],
            'turma': user['turma'],
            'email': user.get('email', 'N/A'),
            'pontos': user['pontos'],
            'descartesAprovados': descartes_user
        })
    
    # Ordenar por pontos
    ranking = sorted(ranking, key=lambda x: x['pontos'], reverse=True)
    
    # Salvar snapshot
    snapshot_ref = db.collection('historico_trimestres').document(f'trimestre_{trimestre}')
    snapshot_ref.set({
        'trimestre': trimestre,
        'dataFechamento': datetime.now(),
        'totalAlunos': len(usuarios),
        'totalDescartes': len(descartes),
        'totalAprovados': len([d for d in descartes if d['status'] == 'Aprovado']),
        'ranking': ranking
    })

def resetar_pontuacao_usuarios():
    """Reseta a pontuação de todos os usuários"""
    if not db:
        return
    
    usuarios_ref = db.collection('usuarios')
    docs = usuarios_ref.stream()
    
    for doc in docs:
        doc.reference.update({'pontos': 0.0})

def get_historico_trimestre(trimestre):
    """Obtém o histórico de um trimestre específico"""
    if not db:
        return None
    
    snapshot_ref = db.collection('historico_trimestres').document(f'trimestre_{trimestre}')
    snapshot_doc = snapshot_ref.get()
    
    if snapshot_doc.exists:
        data = snapshot_doc.to_dict()
        # Converter Timestamp para string
        if 'dataFechamento' in data and hasattr(data['dataFechamento'], 'strftime'):
            data['dataFechamento'] = data['dataFechamento'].strftime('%d/%m/%Y %H:%M')
        return data
    return None

def get_todos_historicos():
    """Obtém todos os históricos de trimestres"""
    if not db:
        return []
    
    historicos = []
    docs = db.collection('historico_trimestres').stream()
    
    for doc in docs:
        data = doc.to_dict()
        if 'dataFechamento' in data and hasattr(data['dataFechamento'], 'strftime'):
            data['dataFechamento'] = data['dataFechamento'].strftime('%d/%m/%Y %H:%M')
        historicos.append(data)
    
    # Ordenar por trimestre
    historicos = sorted(historicos, key=lambda x: x.get('trimestre', 0))
    return historicos

def criar_descarte(usuario_id, numero, linha, material, quantidade, pontos, customizado=False):
    """Cria novo descarte no Firestore"""
    if not db:
        return
    
    descarte_id = int(datetime.now().timestamp() * 1000)
    
    dados = {
        'id': descarte_id,
        'usuarioId': usuario_id,
        'numero': numero,
        'linha': linha,
        'material': material,
        'quantidade': quantidade,
        'pontos': pontos,
        'status': 'Pendente',
        'customizado': customizado,
        'data': datetime.now()
    }
    
    db.collection('descartes').document(str(descarte_id)).set(dados)

def load_descartes():
    """Carrega todos os descartes"""
    if not db:
        return []
    
    descartes = []
    docs = db.collection('descartes').stream()
    
    for doc in docs:
        data = doc.to_dict()
        # Converter Timestamp para string
        if 'data' in data and hasattr(data['data'], 'strftime'):
            data['data'] = data['data'].strftime('%d/%m/%Y %H:%M')
        descartes.append(data)
    
    return descartes

def atualizar_status_descarte(descarte_id, status):
    """Atualiza status do descarte"""
    if not db:
        return
    
    db.collection('descartes').document(str(descarte_id)).update({'status': status})

def criar_resgate(usuario_id, categoria, cupom, codigo, pontos):
    """Cria novo resgate no Firestore"""
    if not db:
        return
    
    resgate_id = int(datetime.now().timestamp() * 1000)
    
    dados = {
        'id': resgate_id,
        'usuarioId': usuario_id,
        'categoria': categoria,
        'cupom': cupom,
        'codigo': codigo,
        'pontos': pontos,
        'status': 'Pendente',
        'data': datetime.now()
    }
    
    db.collection('resgates').document(str(resgate_id)).set(dados)

def load_resgates():
    """Carrega todos os resgates"""
    if not db:
        return []
    
    resgates = []
    docs = db.collection('resgates').stream()
    
    for doc in docs:
        data = doc.to_dict()
        # Converter Timestamp para string
        if 'data' in data and hasattr(data['data'], 'strftime'):
            data['data'] = data['data'].strftime('%d/%m/%Y %H:%M')
        resgates.append(data)
    
    return resgates

def atualizar_status_resgate(resgate_id, status):
    """Atualiza status do resgate"""
    if not db:
        return
    
    db.collection('resgates').document(str(resgate_id)).update({'status': status})

def exportar_backup():
    """Exporta backup completo"""
    backup = {
        'usuarios': load_usuarios(),
        'descartes': load_descartes(),
        'resgates': load_resgates(),
        'data': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    }
    return json.dumps(backup, ensure_ascii=False, indent=2)

# ========================================
# CONFIGURAÇÃO STREAMLIT
# ========================================

st.set_page_config(page_title="Eco Eletrônico", page_icon="♻️", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .stat-card { background: linear-gradient(135deg, #667eea, #764ba2); color: white; 
                 padding: 30px; border-radius: 15px; text-align: center; margin: 20px 0; }
    .stat-card h1 { font-size: 3em; margin: 10px 0; }
    .card-ok { background: #d4edda; border: 2px solid #28a745; padding: 20px; 
               border-radius: 10px; margin: 15px 0; color: #0b3d13; }
    .card-wait { background: #fff3cd; border: 2px solid #ffc107; padding: 20px; 
                 border-radius: 10px; margin: 15px 0; color: #000; }
    .card-info { background: #d1ecf1; border: 2px solid #0c5460; padding: 20px; 
                 border-radius: 10px; margin: 15px 0; color: #0c5460; }
    h1 { color: #ffffff; text-align: center; }
</style>
""", unsafe_allow_html=True)

TURMAS = ['501', '502', '503', '504', '601', '602', '603', '604', '605', '606',
          '701', '702', '703', '704', '705', '706', '707', '708',
          '801', '802', '803', '804', '805', '806', '807',
          '901', '902', '903', '904', '905']

MATERIAIS = {
    'Linha Marrom': {'Televisor': 5, 'Computador': 4, 'Notebook': 3.5, 'Monitor': 3},
    'Linha Azul': {'Liquidificador': 1.5, 'Ferro de Passar': 1, 'Ventilador': 2},
    'Linha Verde': {'Celular': 2.5, 'Bateria': 1.5, 'Carregador': 1, 'Fone de Ouvido': 0.5}
}

CATEGORIAS = {
    'Matemática': [{'nome': 'Cupom Matemática', 'pontos': 45}],
    'Português': [{'nome': 'Cupom Português', 'pontos': 45}],
    'Ciências': [{'nome': 'Cupom Ciências', 'pontos': 40}],
    'Inglês': [{'nome': 'Cupom Inglês', 'pontos': 40}],
    'Ed. Física': [{'nome': 'Cupom Ed. Física', 'pontos': 35}],
    'Artes': [{'nome': 'Cupom Artes', 'pontos': 38}],
    'Geografia': [{'nome': 'Cupom Geografia', 'pontos': 42}],
    'História': [{'nome': 'Cupom História', 'pontos': 48}],
}

ADMIN_PASSWORD = 'soadminpode'

if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.screen = 'home'

# ========================================
# TELAS
# ========================================

def home_screen():
    st.markdown("<h1>♻️ Eco Eletrônico - FECTI 2024</h1>", unsafe_allow_html=True)
    
    if not db:
        st.error("❌ Firestore não configurado!")
        st.info("Configure as credenciais do Firebase")
        return
    
    st.markdown("""<div style='text-align: center; padding: 40px;'>
        <h2 style='color: #ffffff;'>🔐 Sistema com Autenticação Segura!</h2>
        <p style='font-size: 1.2em; color: #ffffff;'>📱 Traga eletrônicos | ⭐ Ganhe pontos | 🎁 Troque por cupons</p>
    </div>""", unsafe_allow_html=True)
    
    try:
        usuarios = load_usuarios()
        st.success(f"✅ Firestore conectado! 👥 {len(usuarios)} alunos cadastrados")
    except Exception as e:
        st.warning(f"⚠️ Carregando... {str(e)}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 Criar Conta", use_container_width=True):
            st.session_state.screen = 'cadastro'
            st.rerun()
    with col2:
        if st.button("🔑 Entrar", use_container_width=True):
            st.session_state.screen = 'login'
            st.rerun()
    with col3:
        if st.button("⚙️ Admin", use_container_width=True):
            st.session_state.screen = 'admin_login'
            st.rerun()

def cadastro_screen():
    st.markdown("<h1>📝 Criar Conta</h1>", unsafe_allow_html=True)
    
    st.markdown("""<div class='card-info'>
        <b>✨ Crie sua conta no Eco Eletrônico!</b><br>
        Você precisará deste e-mail e senha para fazer login no futuro.
    </div>""", unsafe_allow_html=True)
    
    with st.form("form_cadastro"):
        nome = st.text_input("📛 Nome Completo", placeholder="Ex: João Silva")
        turma = st.selectbox("🎓 Turma", ['Selecione...'] + TURMAS)
        email = st.text_input("📧 E-mail", placeholder="seu.email@exemplo.com")
        senha = st.text_input("🔒 Senha (mínimo 6 caracteres)", type="password")
        senha_conf = st.text_input("🔒 Confirme a Senha", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("✅ Criar Conta", use_container_width=True)
        with col2:
            voltar = st.form_submit_button("🔙 Voltar", use_container_width=True)
    
    if submit:
        # Validações
        if not nome.strip():
            st.error("❌ Nome é obrigatório!")
        elif turma == 'Selecione...':
            st.error("❌ Selecione uma turma!")
        elif not email.strip():
            st.error("❌ E-mail é obrigatório!")
        elif not validar_email(email):
            st.error("❌ E-mail inválido!")
        elif not senha:
            st.error("❌ Senha é obrigatória!")
        elif senha != senha_conf:
            st.error("❌ As senhas não coincidem!")
        else:
            with st.spinner("💾 Criando conta..."):
                usuario, mensagem = criar_usuario(nome, turma, email, senha)
                
                if usuario:
                    st.success(f"✅ {mensagem}")
                    st.session_state.user = usuario
                    st.balloons()
                    st.info("🎉 Conta criada! Redirecionando...")
                    st.session_state.screen = 'dashboard'
                    st.rerun()
                else:
                    st.error(f"❌ {mensagem}")
    
    if voltar:
        st.session_state.screen = 'home'
        st.rerun()

def login_screen():
    st.markdown("<h1>🔑 Login</h1>", unsafe_allow_html=True)
    
    st.markdown("""<div class='card-info'>
        <b>👋 Bem-vindo de volta!</b><br>
        Entre com seu e-mail e senha cadastrados.
    </div>""", unsafe_allow_html=True)
    
    with st.form("form_login"):
        email = st.text_input("📧 E-mail", placeholder="seu.email@exemplo.com")
        senha = st.text_input("🔒 Senha", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("🔓 Entrar", use_container_width=True)
        with col2:
            voltar = st.form_submit_button("🔙 Voltar", use_container_width=True)
        
        esqueci = st.form_submit_button("🔑 Esqueci minha senha")
    
    if submit:
        if not email.strip() or not senha:
            st.error("❌ Preencha e-mail e senha!")
        else:
            with st.spinner("🔍 Verificando credenciais..."):
                usuario = buscar_usuario(email, senha)
                
                if usuario:
                    st.success("✅ Login realizado com sucesso!")
                    st.session_state.user = usuario
                    st.session_state.screen = 'dashboard'
                    st.rerun()
                else:
                    st.error("❌ E-mail ou senha incorretos!")
    
    if esqueci:
        st.session_state.screen = 'recuperar_senha'
        st.rerun()
    
    if voltar:
        st.session_state.screen = 'home'
        st.rerun()

def recuperar_senha_screen():
    st.markdown("<h1>🔑 Recuperar Senha</h1>", unsafe_allow_html=True)
    
    if 'etapa_recuperacao' not in st.session_state:
        st.session_state.etapa_recuperacao = 1
        st.session_state.email_recuperacao = ""
        st.session_state.codigo_recuperacao = ""
    
    # ETAPA 1: Solicitar código
    if st.session_state.etapa_recuperacao == 1:
        st.markdown("""<div class='card-info'>
            <b>📧 Digite seu e-mail cadastrado</b><br>
            Você receberá um código para resetar sua senha.
        </div>""", unsafe_allow_html=True)
        
        with st.form("form_solicitar_codigo"):
            email = st.text_input("📧 E-mail", placeholder="seu.email@exemplo.com")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("📨 Solicitar Código", use_container_width=True)
            with col2:
                voltar = st.form_submit_button("🔙 Voltar", use_container_width=True)
        
        if submit:
            if not email.strip():
                st.error("❌ Digite seu e-mail!")
            else:
                with st.spinner("📨 Gerando código..."):
                    codigo, mensagem = recuperar_senha(email)
                    
                    if codigo:
                        st.session_state.email_recuperacao = email
                        st.session_state.codigo_recuperacao = codigo
                        st.session_state.etapa_recuperacao = 2
                        st.success(f"✅ {mensagem}")
                        st.info(f"**Código:** {codigo} (válido por 15 minutos)")
                        st.rerun()
                    else:
                        st.error(f"❌ {mensagem}")
        
        if voltar:
            st.session_state.screen = 'login'
            st.session_state.etapa_recuperacao = 1
            st.rerun()
    
    # ETAPA 2: Resetar senha
    elif st.session_state.etapa_recuperacao == 2:
        st.markdown(f"""<div class='card-info'>
            <b>🔐 Digite o código recebido</b><br>
            E-mail: {st.session_state.email_recuperacao}
        </div>""", unsafe_allow_html=True)
        
        st.info(f"**Seu código:** {st.session_state.codigo_recuperacao}")
        
        with st.form("form_resetar_senha"):
            codigo = st.text_input("🔢 Código de Recuperação")
            senha_nova = st.text_input("🔒 Nova Senha (mínimo 6 caracteres)", type="password")
            senha_conf = st.text_input("🔒 Confirme a Nova Senha", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("✅ Resetar Senha", use_container_width=True)
            with col2:
                cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        if submit:
            if not codigo or not senha_nova:
                st.error("❌ Preencha todos os campos!")
            elif senha_nova != senha_conf:
                st.error("❌ As senhas não coincidem!")
            else:
                with st.spinner("🔄 Resetando senha..."):
                    sucesso, mensagem = resetar_senha_com_codigo(
                        st.session_state.email_recuperacao, 
                        codigo, 
                        senha_nova
                    )
                    
                    if sucesso:
                        st.success(f"✅ {mensagem}")
                        st.balloons()
                        st.session_state.etapa_recuperacao = 1
                        st.session_state.screen = 'login'
                        st.rerun()
                    else:
                        st.error(f"❌ {mensagem}")
        
        if cancelar:
            st.session_state.etapa_recuperacao = 1
            st.session_state.screen = 'login'
            st.rerun()

def consentimento_lgpd_screen():
    """Tela de consentimento LGPD - Primeira vez do usuário"""
    st.markdown("<h1>🌍 Bem-vindo ao Eco Eletrônico!</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea, #764ba2); color: white; 
                padding: 30px; border-radius: 15px; margin: 20px 0;'>
        <h2 style='text-align: center;'>📊 Consentimento para Análise de Dados (LGPD)</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='card-info'>
        <p style='font-size: 1.1em; line-height: 1.8;'>
            Para melhorar nosso sistema e contribuir com estudos ambientais, 
            gostaríamos de coletar dados estatísticos <b>ANÔNIMOS</b> sobre o descarte de eletrônicos.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background: #d4edda; border: 2px solid #28a745; padding: 20px; 
                    border-radius: 10px; margin: 15px 0; min-height: 300px;'>
            <h3 style='color: #155724;'>✅ O que COLETAMOS:</h3>
            <ul style='color: #155724; font-size: 1.05em; line-height: 1.8;'>
                <li>📊 Categorias de eletrônicos descartados</li>
                <li>♻️ Tipos de materiais mais procurados</li>
                <li>📈 Frequência de descarte</li>
                <li>🌍 Impacto ambiental total do programa</li>
                <li>📱 Estatísticas de uso do sistema</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: #f8d7da; border: 2px solid #dc3545; padding: 20px; 
                    border-radius: 10px; margin: 15px 0; min-height: 300px;'>
            <h3 style='color: #721c24;'>❌ O que NÃO COLETAMOS:</h3>
            <ul style='color: #721c24; font-size: 1.05em; line-height: 1.8;'>
                <li>🚫 Nome, e-mail ou dados pessoais</li>
                <li>🚫 Localização precisa</li>
                <li>🚫 Informações identificáveis</li>
                <li>🚫 Histórico de navegação</li>
                <li>🚫 Dados de terceiros</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #11998e, #38ef7d); color: white; 
                padding: 25px; border-radius: 15px; margin: 20px 0;'>
        <h3>🎯 Para que serve?</h3>
        <ul style='font-size: 1.1em; line-height: 1.8;'>
            <li>📚 <b>Educação ambiental:</b> Melhorar o ensino sobre reciclagem</li>
            <li>🌱 <b>Planejamento de reciclagem:</b> Saber quais materiais são mais descartados</li>
            <li>🏭 <b>Produção consciente:</b> Ajudar empresas a produzirem melhor</li>
            <li>🌍 <b>Redução de impactos ambientais:</b> Medir a diferença que fazemos</li>
            <li>💚 <b>Economia sustentável:</b> Contribuir para um futuro melhor</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: #d1ecf1; border: 2px solid #0c5460; padding: 20px; 
                border-radius: 10px; margin: 15px 0;'>
        <h3 style='color: #0c5460;'>🔒 Privacidade Garantida:</h3>
        <ul style='color: #0c5460; font-size: 1.05em; line-height: 1.8;'>
            <li>✅ Dados 100% anônimos e agregados</li>
            <li>✅ Uso exclusivamente estatístico e educacional</li>
            <li>✅ Conformidade total com a LGPD (Lei Geral de Proteção de Dados)</li>
            <li>✅ Pode revogar o consentimento a qualquer momento nas Configurações</li>
            <li>✅ Transparência total: você sempre saberá o que é coletado</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h2 style='color: #ffffff;'>Você autoriza a coleta anônima desses dados?</h2>
        <p style='color: #ffffff; font-size: 1.1em;'>
            <b>Sua escolha não afeta o uso do sistema!</b><br>
            Você pode continuar usando normalmente, independente da resposta.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("✅ SIM, AUTORIZO", use_container_width=True, type="primary"):
            salvar_consentimento(st.session_state.user['id'], True)
            st.success("✅ Obrigado! Sua contribuição ajudará o meio ambiente!")
            st.balloons()
            st.session_state.screen = 'dashboard'
            st.rerun()
    
    with col2:
        if st.button("❌ NÃO, OBRIGADO", use_container_width=True):
            salvar_consentimento(st.session_state.user['id'], False)
            st.info("✅ Tudo bem! Você pode mudar isso depois nas Configurações.")
            st.session_state.screen = 'dashboard'
            st.rerun()
    
    with col3:
        if st.button("📖 Ler mais sobre LGPD", use_container_width=True):
            st.info("""
            A LGPD (Lei Geral de Proteção de Dados) é uma lei brasileira que protege 
            seus dados pessoais. Ela garante que:
            
            • Você saiba o que é coletado
            • Você possa recusar a coleta
            • Seus dados sejam protegidos
            • Você possa pedir a exclusão dos dados
            
            No Eco Eletrônico, levamos isso muito a sério! 🔒
            """)

def dashboard_screen():
    st.markdown("<h1>♻️ Dashboard</h1>", unsafe_allow_html=True)
    st.session_state.user = buscar_usuario_por_id(st.session_state.user['id'])
    
    # Verificar consentimento LGPD
    consentimento = verificar_consentimento(st.session_state.user['id'])
    if consentimento is None:
        st.session_state.screen = 'consentimento_lgpd'
        st.rerun()
        return
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("📱 Cadastrar Eletrônico", use_container_width=True):
            st.session_state.screen = 'cadastrar_eletro'
            st.rerun()
    with col2:
        if st.button("🎁 Cupons", use_container_width=True):
            st.session_state.screen = 'cupons'
            st.rerun()
    with col3:
        if st.button("🎫 Meus Cupons", use_container_width=True):
            st.session_state.screen = 'resgates'
            st.rerun()
    with col4:
        if st.button("⚙️ Configurações", use_container_width=True):
            st.session_state.screen = 'configuracoes'
            st.rerun()
    with col5:
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.user = None
            st.session_state.screen = 'home'
            st.rerun()
    
    st.markdown(f"## 👋 {st.session_state.user['nome']}")
    st.markdown(f"<div class='stat-card'><p>Seus Pontos</p><h1>{st.session_state.user['pontos']:.1f}</h1></div>", unsafe_allow_html=True)
    
    st.markdown("### 📱 Seus Eletrônicos:")
    descartes = [d for d in load_descartes() if d['usuarioId'] == st.session_state.user['id']][:10]
    
    if descartes:
        for d in descartes:
            card = 'card-ok' if d['status'] == 'Aprovado' else 'card-wait'
            icon = '✅' if d['status'] == 'Aprovado' else ('❌' if d['status'] == 'Recusado' else '⏳')
            st.markdown(f"""<div class='{card}'>
                <b>{d['numero']}</b> | {d['material']} ({d['quantidade']} un)<br>
                <b>Pontos:</b> {d['pontos']} | {icon} {d['status']}<br>
                <small>{d['data']}</small></div>""", unsafe_allow_html=True)
    else:
        st.info("Nenhum eletrônico cadastrado")

def configuracoes_screen():
    st.markdown("<h1>⚙️ Configurações</h1>", unsafe_allow_html=True)
    
    user = st.session_state.user
    
    st.markdown(f"""<div class='card-info'>
        <b>👤 Informações da Conta</b><br>
        📛 Nome: {user['nome']}<br>
        🎓 Turma: {user['turma']}<br>
        📧 E-mail: {user.get('email', 'N/A')}<br>
        📅 Cadastro: {user.get('dataCadastro', 'N/A')}
    </div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gerenciar Consentimento LGPD
    st.markdown("### 📊 Privacidade e Dados (LGPD)")
    
    consentimento_atual = verificar_consentimento(user['id'])
    
    if consentimento_atual is None:
        st.warning("⚠️ Você ainda não respondeu sobre o consentimento de dados.")
        if st.button("📋 Ver Termo de Consentimento"):
            st.session_state.screen = 'consentimento_lgpd'
            st.rerun()
    elif consentimento_atual:
        st.success("""
        ✅ **Consentimento Ativo**
        
        Você autorizou a coleta de dados anônimos para fins estatísticos e educacionais.
        Nenhuma informação pessoal é coletada.
        """)
        if st.button("🚫 Revogar Consentimento"):
            salvar_consentimento(user['id'], False)
            st.info("✅ Consentimento revogado com sucesso!")
            st.rerun()
    else:
        st.info("""
        ℹ️ **Consentimento Não Autorizado**
        
        Você optou por não compartilhar dados anônimos.
        Isso não afeta o uso do sistema.
        """)
        if st.button("✅ Autorizar Coleta de Dados Anônimos"):
            salvar_consentimento(user['id'], True)
            st.success("✅ Consentimento concedido com sucesso!")
            st.balloons()
            st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 🔒 Alterar Senha")
    
    with st.form("form_alterar_senha"):
        senha_atual = st.text_input("🔐 Senha Atual", type="password")
        senha_nova = st.text_input("🔒 Nova Senha (mínimo 6 caracteres)", type="password")
        senha_conf = st.text_input("🔒 Confirme a Nova Senha", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("✅ Alterar Senha", use_container_width=True)
        with col2:
            voltar = st.form_submit_button("🔙 Voltar", use_container_width=True)
    
    if submit:
        if not senha_atual or not senha_nova:
            st.error("❌ Preencha todos os campos!")
        elif senha_nova != senha_conf:
            st.error("❌ As senhas não coincidem!")
        else:
            with st.spinner("🔄 Alterando senha..."):
                sucesso, mensagem = alterar_senha(user['id'], senha_atual, senha_nova)
                
                if sucesso:
                    st.success(f"✅ {mensagem}")
                    st.balloons()
                else:
                    st.error(f"❌ {mensagem}")
    
    if voltar:
        st.session_state.screen = 'dashboard'
        st.rerun()

def cadastrar_eletro_screen():
    st.markdown("<h1>♻️ Cadastrar Eletrônico</h1>", unsafe_allow_html=True)
    
    # Mostrar preview de impacto se houver
    if 'preview_impacto' in st.session_state and st.session_state.preview_impacto:
        impacto_html = formatar_impacto_ambiental(st.session_state.preview_impacto)
        if impacto_html:
            st.markdown(impacto_html, unsafe_allow_html=True)
            if st.button("✅ Confirmar Cadastro", use_container_width=True, type="primary"):
                # Finalizar cadastro
                pts = st.session_state.preview_pts
                numero = f"DSC-{int(datetime.now().timestamp() * 1000)}"
                
                with st.spinner("💾 Salvando no Firestore..."):
                    criar_descarte(
                        st.session_state.user['id'], 
                        numero, 
                        st.session_state.preview_linha,
                        st.session_state.preview_material, 
                        st.session_state.preview_qtd, 
                        pts, 
                        st.session_state.preview_customizado
                    )
                    
                    # Registrar no Big Data se consentimento dado
                    consentimento = verificar_consentimento(st.session_state.user['id'])
                    if consentimento and IMPACTO_DISPONIVEL:
                        impacto_data = st.session_state.preview_impacto.copy()
                        impacto_data['categoria'] = st.session_state.preview_linha
                        registrar_evento_anonimo(
                            st.session_state.preview_material,
                            st.session_state.preview_qtd,
                            impacto_data
                        )
                
                st.success(f"✅ {pts} pts cadastrados! (aguardando aprovação)")
                st.balloons()
                
                # Limpar preview
                st.session_state.preview_impacto = None
                st.session_state.screen = 'dashboard'
                st.rerun()
            
            if st.button("🔙 Voltar sem salvar", use_container_width=True):
                st.session_state.preview_impacto = None
                st.rerun()
            
            return
    
    # Formulário normal
    linha = st.selectbox("Linha", ['Selecione...'] + list(MATERIAIS.keys()))
    
    if linha != 'Selecione...':
        materiais = MATERIAIS[linha]
        opcoes = list(materiais.keys()) + ['📝 Outro']
        material_sel = st.selectbox("Material", opcoes,
            format_func=lambda x: f"{x} ({materiais.get(x, '?')}pts)" if x != '📝 Outro' else x)
        
        if material_sel == '📝 Outro':
            material_custom = st.text_input("Digite o material:")
            pontos_custom = st.number_input("Pontos sugeridos:", min_value=0.5, max_value=5.0, value=2.0, step=0.5)
            material_final = material_custom
            pontos_final = pontos_custom
        else:
            material_final = material_sel
            pontos_final = materiais[material_sel]
        
        qtd = st.number_input("Quantidade", min_value=1, value=1)
        
        # Preview do impacto
        if material_final and material_final.strip() and IMPACTO_DISPONIVEL:
            impacto_preview = calcular_impacto_total(material_final, qtd)
            if impacto_preview:
                st.markdown("### 👀 Preview do Impacto:")
                st.info(f"🌱 CO₂ evitado: **{impacto_preview['co2_evitado_kg']:.1f} kg** | "
                       f"⚡ Energia economizada: **{impacto_preview['energia_economizada_kwh']:.1f} kWh** | "
                       f"💧 Água preservada: **{impacto_preview['agua_economizada_litros']:.0f} L**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Ver Impacto Completo e Cadastrar", use_container_width=True, type="primary"):
                if material_final and material_final.strip():
                    pts = pontos_final * qtd
                    
                    # Calcular impacto
                    impacto = calcular_impacto_total(material_final, qtd) if IMPACTO_DISPONIVEL else None
                    
                    # Salvar no session_state para preview
                    st.session_state.preview_impacto = impacto
                    st.session_state.preview_pts = pts
                    st.session_state.preview_linha = linha
                    st.session_state.preview_material = material_final.strip()
                    st.session_state.preview_qtd = qtd
                    st.session_state.preview_customizado = (material_sel == '📝 Outro')
                    
                    if not impacto:
                        # Se não há impacto, cadastrar direto
                        numero = f"DSC-{int(datetime.now().timestamp() * 1000)}"
                        with st.spinner("💾 Salvando no Firestore..."):
                            criar_descarte(st.session_state.user['id'], numero, linha,
                                         material_final.strip(), qtd, pts, material_sel == '📝 Outro')
                        st.success(f"✅ {pts} pts (aguardando aprovação)")
                        st.session_state.screen = 'dashboard'
                    
                    st.rerun()
        with col2:
            if st.button("Voltar", use_container_width=True):
                st.session_state.screen = 'dashboard'
                st.rerun()
    else:
        if st.button("Voltar", use_container_width=True):
            st.session_state.screen = 'dashboard'
            st.rerun()

def cupons_screen():
    st.markdown("<h1>♻️ Cupons</h1>", unsafe_allow_html=True)
    st.session_state.user = buscar_usuario_por_id(st.session_state.user['id'])
    
    # Obter trimestre atual
    trimestre_atual = get_trimestre_atual()
    
    st.info(f"📅 **Trimestre Atual: {trimestre_atual}º**")
    st.markdown(f"### Seus Pontos: {st.session_state.user['pontos']:.1f}")
    
    categorias_compradas = st.session_state.user.get('categoriasCompradas', {'1': [], '2': [], '3': []})
    if not isinstance(categorias_compradas, dict):
        categorias_compradas = {'1': [], '2': [], '3': []}
    
    categorias_trimestre = categorias_compradas.get(str(trimestre_atual), [])
    
    # Avisar quantos cupons já foram comprados
    total_categorias = len(CATEGORIAS)
    comprados = len(categorias_trimestre)
    
    if comprados > 0:
        st.warning(f"⚠️ Você já comprou {comprados}/{total_categorias} cupons neste trimestre")
    
    if comprados == total_categorias:
        st.success("✅ Você comprou todos os cupons deste trimestre! Aguarde o próximo trimestre.")
    
    for cat_nome, cupons in CATEGORIAS.items():
        st.markdown(f"### 🎫 {cat_nome}")
        for cupom in cupons:
            col1, col2 = st.columns([3, 1])
            with col1:
                # Indicar se já foi comprado
                if cat_nome in categorias_trimestre:
                    st.markdown(f"<div class='card-ok'><b>{cupom['nome']}</b> - {cupom['pontos']} pts ✅ <b>Comprado</b></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='card-wait'><b>{cupom['nome']}</b> - {cupom['pontos']} pts</div>", unsafe_allow_html=True)
            with col2:
                # Verificar se já comprou neste trimestre
                pode = cat_nome not in categorias_trimestre
                
                if st.button("Comprar", key=f"c_{cat_nome}_{cupom['nome']}", 
                           use_container_width=True, disabled=not pode):
                    if st.session_state.user['pontos'] < cupom['pontos']:
                        st.error("❌ Pontos insuficientes!")
                    else:
                        with st.spinner("💾 Processando..."):
                            atualizar_pontos(st.session_state.user['id'], -cupom['pontos'])
                            adicionar_categoria_comprada(st.session_state.user['id'], cat_nome, trimestre_atual)
                            codigo = f"CUP-T{trimestre_atual}-{random.randint(1000, 9999)}"
                            criar_resgate(st.session_state.user['id'], cat_nome, cupom['nome'], codigo, cupom['pontos'])
                        st.success(f"✅ Cupom {codigo} solicitado!")
                        st.rerun()
    
    if st.button("🏠 Dashboard", use_container_width=True):
        st.session_state.screen = 'dashboard'
        st.rerun()

def resgates_screen():
    st.markdown("<h1>♻️ Meus Cupons</h1>", unsafe_allow_html=True)
    resgates = [r for r in load_resgates() if r['usuarioId'] == st.session_state.user['id']]
    
    if resgates:
        for r in resgates:
            if r['status'] == 'Aprovado':
                card, status = 'card-ok', '✅ Aprovado!'
            elif r['status'] == 'Recusado':
                card, status = 'card-wait', '❌ Recusado'
            else:
                card, status = 'card-wait', '⏳ Pendente'
            st.markdown(f"""<div class='{card}'>
                <b>🎫 {r['categoria']} - {r['cupom']}</b><br>
                Código: <b style='font-size:24px'>{r['codigo']}</b><br>
                {status}<br><small>{r['data']}</small></div>""", unsafe_allow_html=True)
    else:
        st.info("Nenhum cupom")
    
    if st.button("Voltar", use_container_width=True):
        st.session_state.screen = 'dashboard'
        st.rerun()

def admin_login_screen():
    st.markdown("<h1>🔒 Admin</h1>", unsafe_allow_html=True)
    senha = st.text_input("Senha", type="password")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Entrar", use_container_width=True):
            if senha == ADMIN_PASSWORD:
                st.session_state.screen = 'admin'
                st.rerun()
            else:
                st.error("❌ Senha incorreta!")
    with col2:
        if st.button("Voltar", use_container_width=True):
            st.session_state.screen = 'home'
            st.rerun()

def admin_screen():
    st.markdown("<h1>⚙️ Painel Admin</h1>", unsafe_allow_html=True)
    
    if st.button("🚪 Sair"):
        st.session_state.screen = 'home'
        st.rerun()
    
    usuarios = load_usuarios()
    descartes = load_descartes()
    resgates = load_resgates()
    
    # CONTROLE DE TRIMESTRE
    st.markdown("### 📅 Controle de Trimestre")
    trimestre_atual = get_trimestre_atual()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info(f"**Trimestre Atual: {trimestre_atual}º**")
    with col2:
        if st.button("🔄 Ativar 1º Trimestre", use_container_width=True):
            if trimestre_atual != 1:
                # Salvar snapshot do trimestre atual
                salvar_snapshot_trimestre(trimestre_atual, usuarios, descartes)
                # Resetar pontuação
                resetar_pontuacao_usuarios()
                # Mudar trimestre
                set_trimestre_atual(1)
                st.success("✅ 1º Trimestre ativado! Pontuação resetada!")
                st.rerun()
            else:
                st.warning("⚠️ Já estamos no 1º trimestre!")
    with col3:
        if st.button("🔄 Ativar 2º Trimestre", use_container_width=True):
            if trimestre_atual != 2:
                # Salvar snapshot do trimestre atual
                salvar_snapshot_trimestre(trimestre_atual, usuarios, descartes)
                # Resetar pontuação
                resetar_pontuacao_usuarios()
                # Mudar trimestre
                set_trimestre_atual(2)
                st.success("✅ 2º Trimestre ativado! Pontuação resetada!")
                st.rerun()
            else:
                st.warning("⚠️ Já estamos no 2º trimestre!")
    with col4:
        if st.button("🔄 Ativar 3º Trimestre", use_container_width=True):
            if trimestre_atual != 3:
                # Salvar snapshot do trimestre atual
                salvar_snapshot_trimestre(trimestre_atual, usuarios, descartes)
                # Resetar pontuação
                resetar_pontuacao_usuarios()
                # Mudar trimestre
                set_trimestre_atual(3)
                st.success("✅ 3º Trimestre ativado! Pontuação resetada!")
                st.rerun()
            else:
                st.warning("⚠️ Já estamos no 3º trimestre!")
    
    st.warning("⚠️ **ATENÇÃO:** Ao trocar de trimestre, a pontuação de TODOS os alunos será resetada para 0! O ranking atual será salvo no histórico.")
    
    st.markdown("---")
    
    # HISTÓRICO DE TRIMESTRES
    st.markdown("### 📚 Histórico de Trimestres Anteriores")
    
    historicos = get_todos_historicos()
    
    if historicos:
        for hist in historicos:
            with st.expander(f"📊 {hist['trimestre']}º Trimestre - Encerrado em {hist['dataFechamento']}"):
                st.markdown(f"""
                **Estatísticas:**
                - 👥 Total de alunos: {hist['totalAlunos']}
                - 📱 Total de descartes: {hist['totalDescartes']}
                - ✅ Descartes aprovados: {hist['totalAprovados']}
                """)
                
                st.markdown("#### 🏆 Ranking do Trimestre:")
                
                for i, aluno in enumerate(hist['ranking'][:20], 1):
                    if i == 1:
                        medal = "🥇"
                    elif i == 2:
                        medal = "🥈"
                    elif i == 3:
                        medal = "🥉"
                    else:
                        medal = f"**{i}º**"
                    
                    st.markdown(f"""<div class='card-ok'>
                        {medal} <b>{aluno['nome']}</b> ({aluno['turma']})<br>
                        💎 Pontos: {aluno['pontos']:.1f} | 📱 Descartes: {aluno['descartesAprovados']}
                    </div>""", unsafe_allow_html=True)
                
                if len(hist['ranking']) > 20:
                    with st.expander(f"Ver todos os {len(hist['ranking'])} alunos"):
                        for i, aluno in enumerate(hist['ranking'][20:], 21):
                            st.markdown(f"""<div class='card-wait'>
                                <b>{i}º - {aluno['nome']}</b> ({aluno['turma']})<br>
                                💎 Pontos: {aluno['pontos']:.1f} | 📱 Descartes: {aluno['descartesAprovados']}
                            </div>""", unsafe_allow_html=True)
                
                # Botão para exportar histórico
                backup_hist = json.dumps(hist, ensure_ascii=False, indent=2)
                st.download_button(
                    f"📥 Exportar {hist['trimestre']}º Trimestre",
                    backup_hist,
                    f"trimestre_{hist['trimestre']}_{datetime.now().strftime('%Y%m%d')}.json",
                    "application/json"
                )
    else:
        st.info("Nenhum histórico de trimestre anterior ainda.")
    
    st.markdown("---")
    
    # DASHBOARD DE IMPACTO AMBIENTAL (BIG DATA)
    if IMPACTO_DISPONIVEL:
        st.markdown("### 🌍 IMPACTO AMBIENTAL TOTAL DO PROGRAMA")
        
        stats = get_estatisticas_big_data()
        
        if stats:
            # Métricas principais
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""<div class='stat-card'>
                    <p>Eletrônicos</p>
                    <h1>{stats['total_eventos']}</h1>
                </div>""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"""<div class='stat-card' style='background: linear-gradient(135deg, #11998e, #38ef7d);'>
                    <p>CO₂ Evitado</p>
                    <h1>{stats['total_co2_kg']:.0f}</h1>
                    <p>kg</p>
                </div>""", unsafe_allow_html=True)
            with col3:
                st.markdown(f"""<div class='stat-card' style='background: linear-gradient(135deg, #ee0979, #ff6a00);'>
                    <p>Energia</p>
                    <h1>{stats['total_energia_kwh']:.0f}</h1>
                    <p>kWh</p>
                </div>""", unsafe_allow_html=True)
            with col4:
                st.markdown(f"""<div class='stat-card' style='background: linear-gradient(135deg, #2193b0, #6dd5ed);'>
                    <p>Água</p>
                    <h1>{stats['total_agua_litros']:.0f}</h1>
                    <p>litros</p>
                </div>""", unsafe_allow_html=True)
            
            # Metais pesados evitados
            st.markdown("""
            <div style='background: linear-gradient(135deg, #ee0979, #ff6a00); 
                        color: white; padding: 25px; border-radius: 15px; margin: 20px 0;'>
                <h3>☠️ METAIS PESADOS EVITADOS NO MEIO AMBIENTE</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""<div class='card-ok' style='text-align: center;'>
                    <h2 style='color: #155724;'>🔋 CHUMBO</h2>
                    <h1 style='font-size: 2.5em;'>{stats['total_chumbo_kg']:.2f}</h1>
                    <p><b>kg</b></p>
                    <p style='font-size: 0.9em;'>Contamina solo por 300 anos!</p>
                </div>""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"""<div class='card-ok' style='text-align: center;'>
                    <h2 style='color: #155724;'>☢️ MERCÚRIO</h2>
                    <h1 style='font-size: 2.5em;'>{stats['total_mercurio_kg']:.3f}</h1>
                    <p><b>kg</b></p>
                    <p style='font-size: 0.9em;'>Altamente tóxico!</p>
                </div>""", unsafe_allow_html=True)
            with col3:
                st.markdown(f"""<div class='card-ok' style='text-align: center;'>
                    <h2 style='color: #155724;'>⚠️ CÁDMIO</h2>
                    <h1 style='font-size: 2.5em;'>{stats['total_cadmio_kg']:.2f}</h1>
                    <p><b>kg</b></p>
                    <p style='font-size: 0.9em;'>Causa problemas respiratórios!</p>
                </div>""", unsafe_allow_html=True)
            with col4:
                st.markdown(f"""<div class='card-ok' style='text-align: center;'>
                    <h2 style='color: #155724;'>🔩 NÍQUEL</h2>
                    <h1 style='font-size: 2.5em;'>{stats['total_niquel_kg']:.2f}</h1>
                    <p><b>kg</b></p>
                    <p style='font-size: 0.9em;'>Alergênico e tóxico!</p>
                </div>""", unsafe_allow_html=True)
            
            # Top materiais
            st.markdown("### 📈 Top 10 Materiais Mais Descartados")
            
            if stats['materiais_mais_descartados']:
                for i, (material, qtd) in enumerate(stats['materiais_mais_descartados'][:10], 1):
                    if i <= 3:
                        card_class = 'card-ok'
                        icon = "🥇" if i == 1 else ("🥈" if i == 2 else "🥉")
                    else:
                        card_class = 'card-wait'
                        icon = f"**{i}º**"
                    
                    st.markdown(f"""<div class='{card_class}'>
                        {icon} <b>{material}</b>: {qtd} unidades
                    </div>""", unsafe_allow_html=True)
            
            # Equivalências interessantes
            st.markdown("""
            <div style='background: linear-gradient(135deg, #11998e, #38ef7d); 
                        color: white; padding: 25px; border-radius: 15px; margin: 20px 0;'>
                <h3>🌳 EQUIVALÊNCIAS AMBIENTAIS</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Calcular equivalências
            arvores_plantadas = stats['total_co2_kg'] / 15  # 1 árvore absorve ~15kg CO2/ano
            carros_fora = stats['total_co2_kg'] / 4600  # 1 carro emite ~4600kg CO2/ano
            casas_energia = stats['total_energia_kwh'] / 8760  # 1 casa consome ~8760 kWh/ano
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""<div class='card-info' style='text-align: center;'>
                    <h2>🌳</h2>
                    <h1 style='font-size: 2.5em;'>{arvores_plantadas:.0f}</h1>
                    <p><b>Equivale a plantar árvores</b></p>
                </div>""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"""<div class='card-info' style='text-align: center;'>
                    <h2>🚗</h2>
                    <h1 style='font-size: 2.5em;'>{carros_fora:.1f}</h1>
                    <p><b>Carros fora de circulação por 1 ano</b></p>
                </div>""", unsafe_allow_html=True)
            with col3:
                st.markdown(f"""<div class='card-info' style='text-align: center;'>
                    <h2>🏠</h2>
                    <h1 style='font-size: 2.5em;'>{casas_energia:.1f}</h1>
                    <p><b>Casas abastecidas por 1 ano</b></p>
                </div>""", unsafe_allow_html=True)
            
            # Botão de exportação
            if st.button("📥 Exportar Relatório de Impacto Ambiental (JSON)", use_container_width=True):
                relatorio = json.dumps(stats, ensure_ascii=False, indent=2)
                st.download_button(
                    "💾 Download Relatório",
                    relatorio,
                    f"relatorio_impacto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    "application/json"
                )
        else:
            st.info("📊 Ainda não há dados de impacto ambiental coletados. Aguarde os primeiros descartes!")
    
    st.markdown("---")
    
    # ESTATÍSTICAS GERAIS (TRIMESTRE ATUAL)
    st.markdown(f"### 📊 Estatísticas do {trimestre_atual}º Trimestre (Atual)")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='stat-card'><p>Usuários</p><h1>{len(usuarios)}</h1></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='stat-card'><p>Descartes</p><h1>{len(descartes)}</h1></div>", unsafe_allow_html=True)
    with col3:
        aprovados = len([d for d in descartes if d['status'] == 'Aprovado'])
        st.markdown(f"<div class='stat-card'><p>Aprovados</p><h1>{aprovados}</h1></div>", unsafe_allow_html=True)
    with col4:
        pend = len([r for r in resgates if r['status'] == 'Pendente'])
        st.markdown(f"<div class='stat-card'><p>Cupons Pend.</p><h1>{pend}</h1></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # RANKING ATUAL
    st.markdown(f"### 🏆 Ranking Atual do {trimestre_atual}º Trimestre")
    
    # Ordenar usuários por pontos
    usuarios_ordenados = sorted(usuarios, key=lambda x: x.get('pontos', 0), reverse=True)
    
    # Exibir top 20
    for i, user in enumerate(usuarios_ordenados[:20], 1):
        descartes_user = len([d for d in descartes if d['usuarioId'] == user['id'] and d['status'] == 'Aprovado'])
        
        # Medalhas para top 3
        if i == 1:
            medal = "🥇"
        elif i == 2:
            medal = "🥈"
        elif i == 3:
            medal = "🥉"
        else:
            medal = f"**{i}º**"
        
        st.markdown(f"""<div class='card-ok'>
            {medal} <b>{user['nome']}</b> ({user['turma']}) | 📧 {user.get('email', 'N/A')}<br>
            💎 Pontos: {user['pontos']:.1f} | 📱 Descartes aprovados: {descartes_user}
        </div>""", unsafe_allow_html=True)
    
    if len(usuarios_ordenados) > 20:
        with st.expander(f"📋 Ver todos os {len(usuarios_ordenados)} alunos"):
            for i, user in enumerate(usuarios_ordenados[20:], 21):
                descartes_user = len([d for d in descartes if d['usuarioId'] == user['id'] and d['status'] == 'Aprovado'])
                st.markdown(f"""<div class='card-wait'>
                    <b>{i}º - {user['nome']}</b> ({user['turma']}) | 📧 {user.get('email', 'N/A')}<br>
                    💎 Pontos: {user['pontos']:.1f} | 📱 Descartes: {descartes_user}
                </div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # LISTA DE USUÁRIOS
    st.markdown("### 👥 Lista de Todos os Usuários")
    
    with st.expander("📋 Ver todos os usuários cadastrados"):
        for user in usuarios:
            ativo_badge = "✅ Ativo" if user.get('ativo', True) else "❌ Inativo"
            st.markdown(f"""<div class='card-info'>
                <b>{user['nome']}</b> ({user['turma']})<br>
                📧 {user.get('email', 'N/A')} | 💎 {user['pontos']:.1f} pts<br>
                📅 {user.get('dataCadastro', 'N/A')} | {ativo_badge}
            </div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # BACKUP
    st.markdown("### 💾 Backup Geral")
    if st.button("📥 Exportar Todos os Dados (JSON)", use_container_width=True):
        backup = exportar_backup()
        st.download_button("💾 Download Backup Completo", backup,
            f"backup_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "application/json")
    
    st.markdown("---")
    
    # DESCARTES PENDENTES
    st.markdown("### ⏳ Descartes Pendentes")
    descartes_pend = [d for d in descartes if d['status'] == 'Pendente']
    
    if descartes_pend:
        for d in descartes_pend:
            user = next((u for u in usuarios if u['id'] == d['usuarioId']), None)
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.markdown(f"""<div class='card-wait'>
                    <b>{d['numero']}</b> | {user['nome'] if user else 'N/A'} ({user['turma'] if user else 'N/A'})<br>
                    {d['linha']} | {d['material']} ({d['quantidade']} un) | {d['pontos']} pts
                    </div>""", unsafe_allow_html=True)
            with col2:
                if st.button("✅", key=f"a{d['id']}", use_container_width=True):
                    atualizar_status_descarte(d['id'], 'Aprovado')
                    atualizar_pontos(d['usuarioId'], d['pontos'])
                    st.rerun()
            with col3:
                if st.button("❌", key=f"r{d['id']}", use_container_width=True):
                    atualizar_status_descarte(d['id'], 'Recusado')
                    st.rerun()
    else:
        st.info("Nenhum descarte pendente")
    
    st.markdown("---")
    
    # CUPONS PENDENTES
    st.markdown("### 🎫 Cupons Pendentes")
    cupons_pend = [r for r in resgates if r['status'] == 'Pendente']
    
    if cupons_pend:
        for r in cupons_pend:
            user = next((u for u in usuarios if u['id'] == r['usuarioId']), None)
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"""<div class='card-wait'>
                    <b>{r['codigo']}</b> | {user['nome'] if user else 'N/A'} ({user['turma'] if user else 'N/A'})<br>
                    {r['categoria']} - {r['cupom']} ({r['pontos']} pts)
                    </div>""", unsafe_allow_html=True)
            with col2:
                if st.button("✅", key=f"ac{r['id']}", use_container_width=True):
                    atualizar_status_resgate(r['id'], 'Aprovado')
                    st.rerun()
            with col3:
                if st.button("❌", key=f"rc{r['id']}", use_container_width=True):
                    atualizar_status_resgate(r['id'], 'Recusado')
                    atualizar_pontos(r['usuarioId'], r['pontos'])
                    st.rerun()
    else:
        st.info("Nenhum cupom pendente")

# ========================================
# MAIN
# ========================================

def main():
    screen = st.session_state.get('screen', 'home')
    
    if screen == 'home':
        home_screen()
    elif screen == 'cadastro':
        cadastro_screen()
    elif screen == 'login':
        login_screen()
    elif screen == 'recuperar_senha':
        recuperar_senha_screen()
    elif screen == 'consentimento_lgpd':
        if st.session_state.user:
            consentimento_lgpd_screen()
        else:
            st.session_state.screen = 'home'
            st.rerun()
    elif screen == 'dashboard':
        if st.session_state.user:
            dashboard_screen()
        else:
            st.session_state.screen = 'home'
            st.rerun()
    elif screen == 'configuracoes':
        if st.session_state.user:
            configuracoes_screen()
        else:
            st.session_state.screen = 'home'
            st.rerun()
    elif screen == 'cadastrar_eletro':
        cadastrar_eletro_screen()
    elif screen == 'cupons':
        cupons_screen()
    elif screen == 'resgates':
        resgates_screen()
    elif screen == 'admin_login':
        admin_login_screen()
    elif screen == 'admin':
        admin_screen()
    else:
        st.session_state.screen = 'home'
        st.rerun()

if __name__ == "__main__":
    main()
