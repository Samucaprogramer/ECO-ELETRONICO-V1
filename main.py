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
    """Inicializa Firestore (funciona local e no Streamlit Cloud)"""
    if not firebase_admin._apps:
        try:
            # MODO: Streamlit Cloud (usando st.secrets)
            if "FIREBASE" in st.secrets:
                fb = st.secrets["FIREBASE"]

                key_dict = {
                    "type": fb["type"],
                    "project_id": fb["project_id"],
                    "private_key_id": fb["private_key_id"],
                    "private_key": fb["private_key"],
                    "client_email": fb["client_email"],
                    "client_id": fb["client_id"],
                    "auth_uri": fb["auth_uri"],
                    "token_uri": fb["token_uri"],
                    "auth_provider_x509_cert_url": fb["auth_provider_x509_cert_url"],
                    "client_x509_cert_url": fb["client_x509_cert_url"]
                }

                import tempfile
                import json

                # Criar arquivo .json temporário
                temp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
                temp.write(json.dumps(key_dict).encode())
                temp.close()

                cred = credentials.Certificate(temp.name)

            else:
                # MODO local
                cred = credentials.Certificate("firebase-credentials.json")

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
        'categoriasCompradas': [],
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

def adicionar_categoria_comprada(user_id, categoria):
    """Adiciona categoria comprada"""
    if not db:
        return
    
    user_ref = db.collection('usuarios').document(str(user_id))
    user_doc = user_ref.get()
    
    if user_doc.exists:
        categorias = user_doc.to_dict().get('categoriasCompradas', [])
        if categoria not in categorias:
            categorias.append(categoria)
            user_ref.update({'categoriasCompradas': categorias})

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
    'Direção': [{'nome': 'Brinde', 'pontos': 35}, {'nome': 'Pizza', 'pontos': 50}],
    'Matemática': [{'nome': 'Cupom Matemática', 'pontos': 45}],
    'Português': [{'nome': 'Cupom Português', 'pontos': 45}],
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
    st.markdown(f"### Pontos: {st.session_state.user['pontos']:.1f}")
    
    for cat_nome, cupons in CATEGORIAS.items():
        st.markdown(f"### 🎫 {cat_nome}")
        for cupom in cupons:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"<div class='card-wait'><b>{cupom['nome']}</b> - {cupom['pontos']} pts</div>", unsafe_allow_html=True)
            with col2:
                pode = (cat_nome == 'Direção' or cat_nome not in st.session_state.user.get('categoriasCompradas', []))
                if st.button("Comprar", key=f"c_{cat_nome}_{cupom['nome']}", 
                           use_container_width=True, disabled=not pode):
                    if st.session_state.user['pontos'] < cupom['pontos']:
                        st.error("❌ Pontos insuficientes!")
                    else:
                        with st.spinner("💾 Processando..."):
                            atualizar_pontos(st.session_state.user['id'], -cupom['pontos'])
                            if cat_nome != 'Direção':
                                adicionar_categoria_comprada(st.session_state.user['id'], cat_nome)
                            codigo = f"CUP-{random.randint(1000, 9999)}"
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

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='stat-card'><p>Usuários</p><h1>{len(usuarios)}</h1></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='stat-card'><p>Descartes</p><h1>{len(descartes)}</h1></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='stat-card'><p>Resgates</p><h1>{len(resgates)}</h1></div>", unsafe_allow_html=True)
    with col4:
        if st.download_button("📥 Backup", exportar_backup(), "backup.json"):
            st.success("Backup gerado!")

    st.markdown("## 🟦 Aprovar / Recusar Descates")
    for d in descartes:
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.markdown(
                f"<div class='card-wait'><b>{d['numero']}</b> - {d['material']} "
                f"({d['quantidade']} un) — {d['pontos']} pts<br>"
                f"<small>{d['data']}</small></div>",
                unsafe_allow_html=True
            )
        with col2:
            if st.button("Aprovar", key=f"ap_{d['id']}"):
                atualizar_status_descarte(d['id'], "Aprovado")
                atualizar_pontos(d['usuarioId'], d['pontos'])
                st.rerun()
        with col3:
            if st.button("Recusar", key=f"rec_{d['id']}"):
                atualizar_status_descarte(d['id'], "Recusado")
                st.rerun()

    st.markdown("## 🟦 Aprovar / Recusar Cupons")
    for r in resgates:
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.markdown(
                f"<div class='card-wait'><b>{r['categoria']} — {r['cupom']}</b><br>"
                f"Código: {r['codigo']}<br>"
                f"<small>{r['data']}</small></div>",
                unsafe_allow_html=True
            )
        with col2:
            if st.button("Aprovar", key=f"ra_{r['id']}"):
                atualizar_status_resgate(r['id'], "Aprovado")
                st.rerun()
        with col3:
            if st.button("Recusar", key=f"rr_{r['id']}"):
                atualizar_status_resgate(r['id'], "Recusado")
                st.rerun()


# =====================================================
# FUNÇÃO PRINCIPAL
# =====================================================

def main():
    telas = {
        'home': home_screen,
        'cadastro': cadastro_screen,
        'login': login_screen,
        'dashboard': dashboard_screen,
        'cadastrar_eletro': cadastrar_eletro_screen,
        'cupons': cupons_screen,
        'resgates': resgates_screen,
        'admin_login': admin_login_screen,
        'admin': admin_screen,
    }

    telas[st.session_state.screen]()


if __name__ == "__main__":
    main()
