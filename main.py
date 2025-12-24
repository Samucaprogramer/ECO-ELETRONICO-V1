# main.py - Eco Eletrônico com FIRESTORE (Melhor Performance!)
# Requisitos: pip install streamlit firebase-admin
# Rode: streamlit run main.py

import streamlit as st
from datetime import datetime
import random
import json
import firebase_admin
from firebase_admin import credentials, firestore

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
# FUNÇÕES DE BANCO DE DADOS (FIRESTORE)
# ========================================

def criar_usuario(nome, turma):
    """Cria novo usuário no Firestore"""
    if not db:
        return None
    
    user_id = int(datetime.now().timestamp() * 1000)
    
    dados = {
        'id': user_id,
        'nome': nome,
        'turma': turma,
        'pontos': 0.0,
        'categoriasCompradas': {
            '1': [],  # Trimestre 1
            '2': [],  # Trimestre 2
            '3': []   # Trimestre 3
        },
        'dataCadastro': datetime.now()
    }
    
    # Salva no Firestore
    db.collection('usuarios').document(str(user_id)).set(dados)
    return user_id

def buscar_usuario(nome, turma):
    """Busca usuário por nome e turma"""
    if not db:
        return None
    
    # Query no Firestore
    usuarios_ref = db.collection('usuarios')
    query = usuarios_ref.where('nome', '==', nome).where('turma', '==', turma).limit(1)
    results = query.stream()
    
    for doc in results:
        data = doc.to_dict()
        # Converter Timestamp para string
        if 'dataCadastro' in data and hasattr(data['dataCadastro'], 'strftime'):
            data['dataCadastro'] = data['dataCadastro'].strftime('%d/%m/%Y %H:%M')
        
        # Garantir estrutura de trimestres
        if 'categoriasCompradas' not in data or not isinstance(data['categoriasCompradas'], dict):
            data['categoriasCompradas'] = {'1': [], '2': [], '3': []}
        
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
        <h2 style='color: #ffffff;'>🔥 Dados no Firestore (Google Cloud)!</h2>
        <p style='font-size: 1.2em; color: #ffffff;'>📱 Traga eletrônicos | ⭐ Ganhe pontos | 🎁 Troque por cupons</p>
    </div>""", unsafe_allow_html=True)
    
    try:
        usuarios = load_usuarios()
        st.success(f"✅ Firestore conectado! 👥 {len(usuarios)} alunos cadastrados")
    except Exception as e:
        st.warning(f"⚠️ Carregando... {str(e)}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 Cadastrar", use_container_width=True):
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
    st.markdown("<h1>♻️ Cadastro</h1>", unsafe_allow_html=True)
    nome = st.text_input("Nome Completo")
    turma = st.selectbox("Turma", ['Selecione...'] + TURMAS)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cadastrar", use_container_width=True):
            if not nome.strip() or turma == 'Selecione...':
                st.error("❌ Preencha todos os campos!")
            elif buscar_usuario(nome.strip(), turma):
                st.error("❌ Usuário já existe!")
            else:
                with st.spinner("💾 Salvando no Firestore..."):
                    criar_usuario(nome.strip(), turma)
                    st.session_state.user = buscar_usuario(nome.strip(), turma)
                st.success("✅ Cadastrado!")
                st.session_state.screen = 'dashboard'
                st.rerun()
    with col2:
        if st.button("Voltar", use_container_width=True):
            st.session_state.screen = 'home'
            st.rerun()

def login_screen():
    st.markdown("<h1>♻️ Login</h1>", unsafe_allow_html=True)
    nome = st.text_input("Nome Completo")
    turma = st.selectbox("Turma", ['Selecione...'] + TURMAS)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Entrar", use_container_width=True):
            if not nome.strip() or turma == 'Selecione...':
                st.error("❌ Preencha todos os campos!")
            else:
                with st.spinner("🔍 Buscando no Firestore..."):
                    user = buscar_usuario(nome.strip(), turma)
                    if user:
                        st.session_state.user = user
                        st.session_state.screen = 'dashboard'
                        st.rerun()
                    else:
                        st.error("❌ Usuário não encontrado!")
    with col2:
        if st.button("Voltar", use_container_width=True):
            st.session_state.screen = 'home'
            st.rerun()

def dashboard_screen():
    st.markdown("<h1>♻️ Dashboard</h1>", unsafe_allow_html=True)
    st.session_state.user = buscar_usuario(st.session_state.user['nome'], st.session_state.user['turma'])
    
    col1, col2, col3, col4 = st.columns(4)
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

def cadastrar_eletro_screen():
    st.markdown("<h1>♻️ Cadastrar Eletrônico</h1>", unsafe_allow_html=True)
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
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cadastrar", use_container_width=True):
                if material_final and material_final.strip():
                    pts = pontos_final * qtd
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
    st.session_state.user = buscar_usuario(st.session_state.user['nome'], st.session_state.user['turma'])
    
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
            {medal} <b>{user['nome']}</b> ({user['turma']})<br>
            💎 Pontos: {user['pontos']:.1f} | 📱 Descartes aprovados: {descartes_user}
        </div>""", unsafe_allow_html=True)
    
    if len(usuarios_ordenados) > 20:
        with st.expander(f"📋 Ver todos os {len(usuarios_ordenados)} alunos"):
            for i, user in enumerate(usuarios_ordenados[20:], 21):
                descartes_user = len([d for d in descartes if d['usuarioId'] == user['id'] and d['status'] == 'Aprovado'])
                st.markdown(f"""<div class='card-wait'>
                    <b>{i}º - {user['nome']}</b> ({user['turma']})<br>
                    💎 Pontos: {user['pontos']:.1f} | 📱 Descartes: {descartes_user}
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
    elif screen == 'dashboard':
        if st.session_state.user:
            dashboard_screen()
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
