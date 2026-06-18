# main_com_debug.py
# Use este arquivo TEMPORARIAMENTE para debugar
# Depois volte ao main.py normal

import streamlit as st
from datetime import datetime
import random
import json
import re
import bcrypt
import firebase_admin
from firebase_admin import credentials, firestore
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ========================================
# EMAIL SERVICE (INTEGRADO + DEBUG)
# ========================================

def get_email_config():
    """Obtém configurações de email dos secrets"""
    st.write("🔍 [DEBUG] Procurando email em secrets...")

    try:
        if "email" in st.secrets:
            config = {
                'sender_email': st.secrets["email"]["sender_email"],
                'sender_password': st.secrets["email"]["sender_password"],
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587
            }
            st.success(f"✅ [DEBUG] Email encontrado: {config['sender_email']}")
            return config
        else:
            st.warning("⚠️ [DEBUG] Email NÃO encontrado em secrets!")
            return None
    except Exception as e:
        st.error(f"❌ [DEBUG] Erro ao carregar email: {str(e)}")
        return None


def enviar_codigo_recuperacao(email_destinatario, codigo, nome_usuario=""):
    """Envia email com código de recuperação de senha"""
    st.write(f"📧 [DEBUG] Tentando enviar email para: {email_destinatario}")

    config = get_email_config()
    if not config:
        msg = f"⚠️ Email não configurado. Use código: {codigo}"
        st.warning(msg)
        return False, msg

    try:
        st.write(f"🔌 [DEBUG] Conectando a {config['smtp_server']}:{config['smtp_port']}...")

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "🔐 Código de Recuperação - Eco Eletrônico"
        msg['From'] = config['sender_email']
        msg['To'] = email_destinatario

        html = f"""
        <html>
            <body style="font-family: Arial;">
                <h1 style="color: #22c55e;">♻️ Eco Eletrônico</h1>
                <p>Código: <b>{codigo}</b></p>
                <p>Válido por 15 minutos</p>
            </body>
        </html>
        """

        msg.attach(MIMEText(html, 'html'))

        st.write("🔐 [DEBUG] Conectando e autenticando...")
        with smtplib.SMTP(config['smtp_server'], config['smtp_port'], timeout=15) as server:
            server.starttls()
            st.write("✅ [DEBUG] TLS ativado")

            server.login(config['sender_email'], config['sender_password'])
            st.write("✅ [DEBUG] Login OK")

            server.send_message(msg)
            st.write("✅ [DEBUG] Email enviado!")

        return True, f"✅ Código enviado para {email_destinatario}"

    except smtplib.SMTPAuthenticationError as e:
        st.error(f"❌ [DEBUG] Erro de autenticação: {str(e)}")
        return False, f"Erro de autenticação: {str(e)}"
    except smtplib.SMTPException as e:
        st.error(f"❌ [DEBUG] Erro SMTP: {str(e)}")
        return False, f"Erro SMTP: {str(e)}"
    except Exception as e:
        st.error(f"❌ [DEBUG] Erro desconhecido: {str(e)}")
        return False, f"Erro: {str(e)}"


def enviar_confirmacao_senha_alterada(email_destinatario, nome_usuario=""):
    """Envia email de confirmação"""
    try:
        config = get_email_config()
        if not config:
            return False, "Email não configurado"

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "✅ Senha Alterada - Eco Eletrônico"
        msg['From'] = config['sender_email']
        msg['To'] = email_destinatario

        html = f"""
        <html>
            <body style="font-family: Arial;">
                <h1 style="color: #22c55e;">✅ Senha Alterada!</h1>
                <p>Sua senha foi alterada com sucesso.</p>
            </body>
        </html>
        """

        msg.attach(MIMEText(html, 'html'))

        with smtplib.SMTP(config['smtp_server'], config['smtp_port'], timeout=15) as server:
            server.starttls()
            server.login(config['sender_email'], config['sender_password'])
            server.send_message(msg)

        return True, "Email de confirmação enviado"
    except Exception as e:
        return False, f"Erro: {str(e)}"


# ========================================
# FIREBASE
# ========================================

@st.cache_resource
def init_firestore():
    if not firebase_admin._apps:
        try:
            if "firebase" in st.secrets:
                if isinstance(st.secrets["firebase"]["key"], str):
                    key_dict = json.loads(st.secrets["firebase"]["key"])
                else:
                    key_dict = dict(st.secrets["firebase"]["key"])
                cred = credentials.Certificate(key_dict)
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
# VALIDAÇÃO
# ========================================

def validar_email(email):
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(padrao, email) is not None


def validar_senha(senha):
    if len(senha) < 6:
        return False, "Mínimo 6 caracteres"
    return True, "OK"


def hash_senha(senha):
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verificar_senha(senha, hash_armazenado):
    return bcrypt.checkpw(senha.encode('utf-8'), hash_armazenado.encode('utf-8'))


# ========================================
# AUTENTICAÇÃO
# ========================================

def email_existe(email):
    if not db:
        return False
    usuarios_ref = db.collection('usuarios')
    query = usuarios_ref.where('email', '==', email.lower()).limit(1)
    results = list(query.stream())
    return len(results) > 0


def criar_usuario(nome, turma, email, senha):
    if not db:
        return None, "Firestore desconectado"

    if not nome.strip():
        return None, "Nome obrigatório"
    if not validar_email(email):
        return None, "Email inválido"

    valido, msg = validar_senha(senha)
    if not valido:
        return None, msg
    if email_existe(email):
        return None, "Email já cadastrado"

    user_id = int(datetime.now().timestamp() * 1000)
    senha_hash = hash_senha(senha)

    dados = {
        'id': user_id,
        'nome': nome.strip(),
        'turma': turma,
        'email': email.lower().strip(),
        'senha': senha_hash,
        'pontos': 0.0,
        'categoriasCompradas': {'1': [], '2': [], '3': []},
        'dataCadastro': datetime.now(),
        'ativo': True
    }

    db.collection('usuarios').document(str(user_id)).set(dados)
    dados_retorno = dados.copy()
    del dados_retorno['senha']
    return dados_retorno, "Conta criada!"


def buscar_usuario(email, senha):
    if not db or not validar_email(email):
        return None

    usuarios_ref = db.collection('usuarios')
    query = usuarios_ref.where('email', '==', email.lower()).limit(1)
    results = list(query.stream())

    if not results:
        return None

    user_data = results[0].to_dict()

    if not user_data.get('ativo', True):
        return None
    if not verificar_senha(senha, user_data['senha']):
        return None

    if 'dataCadastro' in user_data and hasattr(user_data['dataCadastro'], 'strftime'):
        user_data['dataCadastro'] = user_data['dataCadastro'].strftime('%d/%m/%Y %H:%M')

    if 'categoriasCompradas' not in user_data:
        user_data['categoriasCompradas'] = {'1': [], '2': [], '3': []}

    if 'senha' in user_data:
        del user_data['senha']

    return user_data


def recuperar_senha(email):
    if not db or not validar_email(email):
        return None, "Email inválido"

    usuarios_ref = db.collection('usuarios')
    query = usuarios_ref.where('email', '==', email.lower()).limit(1)
    results = list(query.stream())

    if not results:
        return None, "Email não encontrado"

    user_data = results[0].to_dict()
    codigo = f"{random.randint(100000, 999999)}"
    user_doc = results[0]
    user_doc.reference.update({
        'codigoRecuperacao': codigo,
        'codigoExpiracao': datetime.now().timestamp() + 900
    })

    st.write(f"🔍 [DEBUG] Código gerado: {codigo}")

    # TENTAR ENVIAR EMAIL
    sucesso, msg = enviar_codigo_recuperacao(email.lower(), codigo, user_data.get('nome', 'Usuário'))

    st.write(f"📧 [DEBUG] Resultado: {msg}")

    if sucesso:
        return codigo, msg
    else:
        return codigo, f"⚠️ {msg}"


def resetar_senha_com_codigo(email, codigo, senha_nova):
    if not db:
        return False, "Firestore desconectado"

    usuarios_ref = db.collection('usuarios')
    query = usuarios_ref.where('email', '==', email.lower()).limit(1)
    results = list(query.stream())

    if not results:
        return False, "Email não encontrado"

    user_data = results[0].to_dict()
    user_ref = results[0].reference

    if 'codigoRecuperacao' not in user_data:
        return False, "Nenhum código solicitado"
    if user_data['codigoRecuperacao'] != codigo:
        return False, "Código incorreto"
    if datetime.now().timestamp() > user_data.get('codigoExpiracao', 0):
        return False, "Código expirado"

    valido, msg = validar_senha(senha_nova)
    if not valido:
        return False, msg

    novo_hash = hash_senha(senha_nova)
    user_ref.update({
        'senha': novo_hash,
        'codigoRecuperacao': firestore.DELETE_FIELD,
        'codigoExpiracao': firestore.DELETE_FIELD
    })

    enviar_confirmacao_senha_alterada(email.lower(), user_data.get('nome', 'Usuário'))

    return True, "✅ Senha resetada! Verifique seu email."


# ========================================
# CONFIG STREAMLIT
# ========================================

st.set_page_config(page_title="Eco Eletrônico", page_icon="♻️", layout="wide")

st.markdown("""
<style>
    .stApp { background: #1a1a1a; }
    h1, h2, h3, p { color: #ffffff; }
</style>
""", unsafe_allow_html=True)

TURMAS = ['501', '502', '503', '504']

if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.screen = 'home'


# ========================================
# TELAS
# ========================================

def home_screen():
    st.markdown("<h1 style='text-align: center; color: #22c55e;'>♻️ Eco Eletrônico - DEBUG</h1>",
                unsafe_allow_html=True)

    st.warning("⚠️ MODO DEBUG ATIVADO - Todas as ações serão logadas na tela")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Criar Conta", use_container_width=True):
            st.session_state.screen = 'cadastro'
            st.rerun()
    with col2:
        if st.button("Login", use_container_width=True):
            st.session_state.screen = 'login'
            st.rerun()
    with col3:
        if st.button("Recuperar Senha", use_container_width=True):
            st.session_state.screen = 'recuperar'
            st.rerun()


def recuperar_screen():
    st.markdown("<h1 style='color: #22c55e;'>Recuperar Senha - DEBUG</h1>", unsafe_allow_html=True)

    st.info("ℹ️ Veja os logs abaixo enquanto processa")

    with st.form("recuperar"):
        email = st.text_input("Email:")
        submit = st.form_submit_button("Recuperar", use_container_width=True)
        voltar = st.form_submit_button("Voltar", use_container_width=True)

    if submit:
        if not email:
            st.error("Digite email!")
        else:
            st.markdown("---")
            st.markdown("### 🔍 PROCESSANDO...")
            st.markdown("---")

            codigo, mensagem = recuperar_senha(email)

            st.markdown("---")
            st.markdown("### ✅ RESULTADO")
            st.markdown("---")

            if codigo:
                st.success(f"✅ {mensagem}")
                st.info(f"Código: **{codigo}** (para teste manual)")
            else:
                st.error(f"❌ {mensagem}")

    if voltar:
        st.session_state.screen = 'home'
        st.rerun()


def cadastro_screen():
    st.markdown("<h1 style='color: #22c55e;'>Criar Conta</h1>", unsafe_allow_html=True)

    with st.form("cadastro"):
        nome = st.text_input("Nome:")
        turma = st.selectbox("Turma:", TURMAS)
        email = st.text_input("Email:")
        senha = st.text_input("Senha:", type="password")

        submit = st.form_submit_button("Criar", use_container_width=True)
        voltar = st.form_submit_button("Voltar", use_container_width=True)

    if submit:
        usuario, msg = criar_usuario(nome, turma, email, senha)
        if usuario:
            st.success(f"✅ {msg}")
            st.session_state.user = usuario
            st.session_state.screen = 'home'
            st.rerun()
        else:
            st.error(f"❌ {msg}")

    if voltar:
        st.session_state.screen = 'home'
        st.rerun()


def login_screen():
    st.markdown("<h1 style='color: #22c55e;'>Login</h1>", unsafe_allow_html=True)

    with st.form("login"):
        email = st.text_input("Email:")
        senha = st.text_input("Senha:", type="password")

        submit = st.form_submit_button("Entrar", use_container_width=True)
        voltar = st.form_submit_button("Voltar", use_container_width=True)

    if submit:
        usuario = buscar_usuario(email, senha)
        if usuario:
            st.success("✅ Login OK!")
            st.session_state.user = usuario
            st.session_state.screen = 'dashboard'
            st.rerun()
        else:
            st.error("❌ Credenciais inválidas!")

    if voltar:
        st.session_state.screen = 'home'
        st.rerun()


def dashboard_screen():
    st.markdown(f"<h1 style='color: #22c55e;'>Bem-vindo, {st.session_state.user['nome']}!</h1>", unsafe_allow_html=True)

    if st.button("Sair", use_container_width=True):
        st.session_state.user = None
        st.session_state.screen = 'home'
        st.rerun()


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
    elif screen == 'recuperar':
        recuperar_screen()
    elif screen == 'dashboard':
        dashboard_screen()


if __name__ == "__main__":
    main()
