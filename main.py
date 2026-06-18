# main.py - Eco Eletrônico COM TURMAS ATUALIZADAS
# Turmas: 601-607, 701-707, 801-808, 901-906

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
# EMAIL SERVICE (INTEGRADO)
# ========================================

def get_email_config():
    """Obtém configurações de email dos secrets"""
    try:
        if "email" in st.secrets:
            return {
                'sender_email': st.secrets["email"]["sender_email"],
                'sender_password': st.secrets["email"]["sender_password"],
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587
            }
        return None
    except Exception as e:
        return None

def enviar_codigo_recuperacao(email_destinatario, codigo, nome_usuario=""):
    """Envia email com código de recuperação de senha"""
    config = get_email_config()
    if not config:
        return False, "⚠️ Email não configurado. Use código: " + codigo
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "🔐 Código de Recuperação de Senha - Eco Eletrônico"
        msg['From'] = config['sender_email']
        msg['To'] = email_destinatario
        
        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; background: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #1a1a1a, #2d2d2d); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
                    .content {{ background: white; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .codigo {{ background: #22c55e; color: #1a1a1a; padding: 20px; border-radius: 10px; font-size: 28px; font-weight: bold; text-align: center; margin: 20px 0; letter-spacing: 5px; }}
                    .aviso {{ background: #fff3cd; color: #856404; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107; }}
                    .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
                    h1 {{ color: #22c55e; margin: 0; }}
                    p {{ color: #333; line-height: 1.6; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>♻️ Eco Eletrônico</h1>
                        <p>Recuperação de Senha</p>
                    </div>
                    <div class="content">
                        <p>Olá <b>{nome_usuario if nome_usuario else 'Usuário'}</b>,</p>
                        
                        <p>Você solicitou a recuperação de senha no <b>Eco Eletrônico</b>.</p>
                        
                        <p>Use o código abaixo para redefinir sua senha:</p>
                        
                        <div class="codigo">{codigo}</div>
                        
                        <div class="aviso">
                            <strong>⏰ Atenção!</strong><br>
                            Este código expira em <strong>15 minutos</strong>
                        </div>
                        
                        <p><strong>Como usar:</strong></p>
                        <ol>
                            <li>Acesse o formulário de recuperação de senha</li>
                            <li>Cole o código acima</li>
                            <li>Digite sua nova senha</li>
                            <li>Confirme a nova senha</li>
                        </ol>
                        
                        <p style="color: #666; font-size: 13px; margin-top: 30px;">
                            <strong>Não solicitou essa recuperação?</strong><br>
                            Ignore este email. Sua conta está segura.
                        </p>
                    </div>
                    <div class="footer">
                        <p>© 2024 Eco Eletrônico - Plataforma de Sustentabilidade</p>
                        <p>Este é um email automático, não responda.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['sender_email'], config['sender_password'])
            server.send_message(msg)
        
        return True, f"✅ Código enviado para {email_destinatario}"
    
    except Exception as e:
        return False, f"⚠️ Erro ao enviar: {str(e)}"

def enviar_confirmacao_senha_alterada(email_destinatario, nome_usuario=""):
    """Envia email de confirmação após alterar senha"""
    config = get_email_config()
    if not config:
        return False, "Email não configurado"
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "✅ Senha Alterada com Sucesso - Eco Eletrônico"
        msg['From'] = config['sender_email']
        msg['To'] = email_destinatario
        
        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; background: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #22c55e, #16a34a); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
                    .content {{ background: white; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .sucesso {{ background: #d4edda; color: #155724; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745; }}
                    .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
                    h1 {{ color: #22c55e; margin: 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>♻️ Eco Eletrônico</h1>
                        <p>Confirmação de Alteração</p>
                    </div>
                    <div class="content">
                        <p>Olá <b>{nome_usuario if nome_usuario else 'Usuário'}</b>,</p>
                        
                        <div class="sucesso">
                            <strong>✅ Sua senha foi alterada com sucesso!</strong>
                        </div>
                        
                        <p>Você agora pode fazer login no <b>Eco Eletrônico</b> com sua nova senha.</p>
                        
                        <p><strong>Informações da alteração:</strong></p>
                        <ul>
                            <li>Email: {email_destinatario}</li>
                            <li>Data: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</li>
                            <li>Status: ✅ Alterada com sucesso</li>
                        </ul>
                    </div>
                    <div class="footer">
                        <p>© 2024 Eco Eletrônico - Plataforma de Sustentabilidade</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['sender_email'], config['sender_password'])
            server.send_message(msg)
        
        return True, "✅ Email de confirmação enviado"
    
    except Exception as e:
        return False, f"Erro ao enviar confirmação"

# ========================================
# CONFIGURAÇÃO DO FIRESTORE
# ========================================

@st.cache_resource
def init_firestore():
    """Inicializa Firestore (funciona local E no Streamlit Cloud)"""
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
# FUNÇÕES DE VALIDAÇÃO E SEGURANÇA
# ========================================

def validar_email(email):
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(padrao, email) is not None

def validar_senha(senha):
    if len(senha) < 6:
        return False, "A senha deve ter no mínimo 6 caracteres"
    return True, "Senha válida"

def hash_senha(senha):
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verificar_senha(senha, hash_armazenado):
    return bcrypt.checkpw(senha.encode('utf-8'), hash_armazenado.encode('utf-8'))

# ========================================
# FUNÇÕES DE AUTENTICAÇÃO
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
        return None, "Erro: Firestore não conectado"
    
    if not nome.strip():
        return None, "Nome é obrigatório"
    if not validar_email(email):
        return None, "E-mail inválido"
    
    valido, msg = validar_senha(senha)
    if not valido:
        return None, msg
    if email_existe(email):
        return None, "E-mail já cadastrado"
    
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
    return dados_retorno, "Usuário criado com sucesso"

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
    
    if 'categoriasCompradas' not in user_data or not isinstance(user_data['categoriasCompradas'], dict):
        user_data['categoriasCompradas'] = {'1': [], '2': [], '3': []}
    
    if 'senha' in user_data:
        del user_data['senha']
    
    return user_data

def alterar_senha(user_id, senha_atual, senha_nova):
    if not db:
        return False, "Erro: Firestore não conectado"
    
    user_ref = db.collection('usuarios').document(str(user_id))
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        return False, "Usuário não encontrado"
    
    user_data = user_doc.to_dict()
    
    if not verificar_senha(senha_atual, user_data['senha']):
        return False, "Senha atual incorreta"
    
    valido, msg = validar_senha(senha_nova)
    if not valido:
        return False, msg
    
    novo_hash = hash_senha(senha_nova)
    user_ref.update({'senha': novo_hash})
    
    enviar_confirmacao_senha_alterada(
        user_data.get('email', ''),
        user_data.get('nome', 'Usuário')
    )
    
    return True, "✅ Senha alterada com sucesso! Verifique seu email."

def recuperar_senha(email):
    if not db or not validar_email(email):
        return None, "E-mail inválido"
    
    usuarios_ref = db.collection('usuarios')
    query = usuarios_ref.where('email', '==', email.lower()).limit(1)
    results = list(query.stream())
    
    if not results:
        return None, "E-mail não encontrado"
    
    user_data = results[0].to_dict()
    codigo = f"{random.randint(100000, 999999)}"
    user_doc = results[0]
    user_doc.reference.update({
        'codigoRecuperacao': codigo,
        'codigoExpiracao': datetime.now().timestamp() + 900
    })
    
    sucesso, msg = enviar_codigo_recuperacao(
        email.lower(),
        codigo,
        user_data.get('nome', 'Usuário')
    )
    
    if sucesso:
        return codigo, msg
    else:
        return codigo, f"⚠️ {msg}\n\n**Código de fallback:** {codigo}"

def resetar_senha_com_codigo(email, codigo, senha_nova):
    if not db:
        return False, "Erro: Firestore não conectado"
    
    usuarios_ref = db.collection('usuarios')
    query = usuarios_ref.where('email', '==', email.lower()).limit(1)
    results = list(query.stream())
    
    if not results:
        return False, "E-mail não encontrado"
    
    user_data = results[0].to_dict()
    user_ref = results[0].reference
    
    if 'codigoRecuperacao' not in user_data:
        return False, "Nenhum código de recuperação solicitado"
    if user_data['codigoRecuperacao'] != codigo:
        return False, "Código incorreto"
    if datetime.now().timestamp() > user_data.get('codigoExpiracao', 0):
        return False, "Código expirado. Solicite um novo código"
    
    valido, msg = validar_senha(senha_nova)
    if not valido:
        return False, msg
    
    novo_hash = hash_senha(senha_nova)
    user_ref.update({
        'senha': novo_hash,
        'codigoRecuperacao': firestore.DELETE_FIELD,
        'codigoExpiracao': firestore.DELETE_FIELD
    })
    
    enviar_confirmacao_senha_alterada(
        email.lower(),
        user_data.get('nome', 'Usuário')
    )
    
    return True, "✅ Senha resetada com sucesso! Verifique seu email."

# ========================================
# FUNÇÕES DE BANCO DE DADOS (FIRESTORE)
# ========================================

def buscar_usuario_por_id(user_id):
    if not db:
        return None
    user_ref = db.collection('usuarios').document(str(user_id))
    user_doc = user_ref.get()
    
    if user_doc.exists:
        data = user_doc.to_dict()
        if 'dataCadastro' in data and hasattr(data['dataCadastro'], 'strftime'):
            data['dataCadastro'] = data['dataCadastro'].strftime('%d/%m/%Y %H:%M')
        if 'categoriasCompradas' not in data or not isinstance(data['categoriasCompradas'], dict):
            data['categoriasCompradas'] = {'1': [], '2': [], '3': []}
        if 'senha' in data:
            del data['senha']
        return data
    return None

def load_usuarios():
    if not db:
        return []
    usuarios = []
    docs = db.collection('usuarios').stream()
    for doc in docs:
        data = doc.to_dict()
        if 'dataCadastro' in data and hasattr(data['dataCadastro'], 'strftime'):
            data['dataCadastro'] = data['dataCadastro'].strftime('%d/%m/%Y %H:%M')
        if 'categoriasCompradas' not in data or not isinstance(data['categoriasCompradas'], dict):
            data['categoriasCompradas'] = {'1': [], '2': [], '3': []}
        if 'senha' in data:
            del data['senha']
        usuarios.append(data)
    return usuarios

def atualizar_pontos(user_id, pontos_adicionar):
    if not db:
        return
    user_ref = db.collection('usuarios').document(str(user_id))
    user_doc = user_ref.get()
    if user_doc.exists:
        pontos_atuais = user_doc.to_dict().get('pontos', 0)
        novos_pontos = pontos_atuais + pontos_adicionar
        user_ref.update({'pontos': novos_pontos})

def adicionar_categoria_comprada(user_id, categoria, trimestre):
    if not db:
        return
    user_ref = db.collection('usuarios').document(str(user_id))
    user_doc = user_ref.get()
    if user_doc.exists:
        data = user_doc.to_dict()
        categorias = data.get('categoriasCompradas', {'1': [], '2': [], '3': []})
        if not isinstance(categorias, dict):
            categorias = {'1': [], '2': [], '3': []}
        trimestre_str = str(trimestre)
        if trimestre_str not in categorias:
            categorias[trimestre_str] = []
        if categoria not in categorias[trimestre_str]:
            categorias[trimestre_str].append(categoria)
            user_ref.update({'categoriasCompradas': categorias})

def get_trimestre_atual():
    if not db:
        return 1
    config_ref = db.collection('config').document('sistema')
    config_doc = config_ref.get()
    if config_doc.exists:
        return config_doc.to_dict().get('trimestreAtual', 1)
    else:
        config_ref.set({'trimestreAtual': 1})
        return 1

def set_trimestre_atual(trimestre):
    if not db:
        return
    config_ref = db.collection('config').document('sistema')
    config_ref.set({'trimestreAtual': trimestre})

def criar_descarte(usuario_id, numero, linha, material, quantidade, pontos, customizado=False):
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
    if not db:
        return []
    descartes = []
    docs = db.collection('descartes').stream()
    for doc in docs:
        data = doc.to_dict()
        if 'data' in data and hasattr(data['data'], 'strftime'):
            data['data'] = data['data'].strftime('%d/%m/%Y %H:%M')
        descartes.append(data)
    return descartes

def atualizar_status_descarte(descarte_id, status):
    if not db:
        return
    db.collection('descartes').document(str(descarte_id)).update({'status': status})

def criar_resgate(usuario_id, categoria, cupom, codigo, pontos):
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
    if not db:
        return []
    resgates = []
    docs = db.collection('resgates').stream()
    for doc in docs:
        data = doc.to_dict()
        if 'data' in data and hasattr(data['data'], 'strftime'):
            data['data'] = data['data'].strftime('%d/%m/%Y %H:%M')
        resgates.append(data)
    return resgates

def atualizar_status_resgate(resgate_id, status):
    if not db:
        return
    db.collection('resgates').document(str(resgate_id)).update({'status': status})

# ========================================
# CONFIGURAÇÃO STREAMLIT
# ========================================

st.set_page_config(page_title="Eco Eletrônico", page_icon="♻️", layout="wide")

st.markdown("""
<style>
    .stApp { background: #1a1a1a; }
    .stat-card {
        background: linear-gradient(135deg, #2d2d2d, #1a1a1a);
        color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
        border: 3px solid #22c55e;
    }
    .stat-card h1 { font-size: 3em; margin: 10px 0; color: #22c55e; }
    .stat-card p { font-size: 1.2em; opacity: 0.9; color: #ffffff; }
    .card-ok { background: #22c55e; color: #1a1a1a; padding: 15px; border-radius: 8px; margin: 8px 0; font-weight: bold; }
    .card-wait { background: #3a3a3a; color: #ffffff; padding: 15px; border-radius: 8px; margin: 8px 0; border-left: 3px solid #22c55e; }
    .card-info { background: #ffffff; color: #1a1a1a; padding: 15px; border-radius: 8px; margin: 8px 0; border-left: 3px solid #22c55e; }
    h1, h2, h3 { color: #ffffff; }
    p, label { color: #ffffff; }
    .stMarkdown { color: #ffffff; }
    .stTextInput input, .stSelectbox select, .stNumberInput input {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 2px solid #22c55e;
    }
    .stTextInput input:focus, .stSelectbox select:focus, .stNumberInput input:focus {
        border: 2px solid #22c55e;
        background-color: #3a3a3a;
    }
    .stButton button {
        background: #22c55e;
        color: #1a1a1a;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton button:hover {
        background: #16a34a;
        transform: scale(1.02);
    }
    .stForm {
        background: #2d2d2d;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border: 2px solid #22c55e;
    }
    .stSuccess { background-color: #22c55e !important; color: #1a1a1a !important; border-radius: 8px; }
    .stError { background-color: #dc2626 !important; color: #ffffff !important; border-radius: 8px; }
    .stWarning { background-color: #f59e0b !important; color: #1a1a1a !important; border-radius: 8px; }
    .stInfo { background-color: #3a3a3a !important; color: #ffffff !important; border: 2px solid #22c55e !important; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ========================================
# TURMAS ATUALIZADAS
# ========================================

TURMAS = ['601', '602', '603', '604', '605', '606', '607',
          '701', '702', '703', '704', '705', '706', '707',
          '801', '802', '803', '804', '805', '806', '807', '808',
          '901', '902', '903', '904', '905', '906']

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
    st.markdown("<h1 style='text-align: center; color: #22c55e;'>♻️ Eco Eletrônico</h1>", unsafe_allow_html=True)
    
    if not db:
        st.error("❌ Firestore não configurado!")
        return
    
    st.markdown("""<div style='text-align: center; padding: 40px;'>
        <h2 style='color: #ffffff;'>🔐 Sistema com Autenticação Segura!</h2>
        <p style='font-size: 1.2em; color: #ffffff;'>📱 Traga eletrônicos | ⭐ Ganhe pontos | 🎁 Troque por cupons</p>
    </div>""", unsafe_allow_html=True)
    
    try:
        usuarios = load_usuarios()
        st.success(f"✅ Firestore conectado! 👥 {len(usuarios)} alunos cadastrados")
    except Exception as e:
        st.warning(f"⚠️ Carregando...")
    
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
    st.markdown("<h1 style='color: #22c55e;'>📝 Criar Conta</h1>", unsafe_allow_html=True)
    
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
    st.markdown("<h1 style='color: #22c55e;'>🔑 Login</h1>", unsafe_allow_html=True)
    
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
    st.markdown("<h1 style='color: #22c55e;'>🔑 Recuperar Senha</h1>", unsafe_allow_html=True)
    
    if 'etapa_recuperacao' not in st.session_state:
        st.session_state.etapa_recuperacao = 1
        st.session_state.email_recuperacao = ""
        st.session_state.codigo_recuperacao = ""
    
    if st.session_state.etapa_recuperacao == 1:
        st.markdown("""<div class='card-info'>
            <b>📧 Digite seu e-mail cadastrado</b><br>
            Você receberá um código por email para resetar sua senha.
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
                with st.spinner("📨 Gerando e enviando código..."):
                    codigo, mensagem = recuperar_senha(email)
                    
                    if codigo:
                        st.session_state.email_recuperacao = email
                        st.session_state.codigo_recuperacao = codigo
                        st.session_state.etapa_recuperacao = 2
                        st.success(f"✅ {mensagem}")
                        st.info("⏰ **Código válido por 15 minutos**")
                        st.rerun()
                    else:
                        st.error(f"❌ {mensagem}")
        
        if voltar:
            st.session_state.screen = 'login'
            st.session_state.etapa_recuperacao = 1
            st.rerun()
    
    elif st.session_state.etapa_recuperacao == 2:
        st.markdown(f"""<div class='card-info'>
            <b>🔐 Digite o código recebido no seu email</b><br>
            E-mail: {st.session_state.email_recuperacao}
        </div>""", unsafe_allow_html=True)
        
        st.info("📧 Verifique seu email (incluindo spam) para o código de 6 dígitos")
        
        with st.form("form_resetar_senha"):
            codigo = st.text_input("🔢 Código de Recuperação (6 dígitos)")
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

def dashboard_screen():
    st.markdown("<h1 style='color: #22c55e;'>♻️ Dashboard</h1>", unsafe_allow_html=True)
    st.session_state.user = buscar_usuario_por_id(st.session_state.user['id'])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("📱 Cadastrar", use_container_width=True):
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
        if st.button("⚙️ Config", use_container_width=True):
            st.session_state.screen = 'configuracoes'
            st.rerun()
    with col5:
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.user = None
            st.session_state.screen = 'home'
            st.rerun()
    
    st.markdown(f"## 👋 {st.session_state.user['nome']}")
    st.markdown(f"<div class='stat-card'><p>Seus Pontos</p><h1>{st.session_state.user['pontos']:.1f}</h1></div>", unsafe_allow_html=True)

def configuracoes_screen():
    st.markdown("<h1 style='color: #22c55e;'>⚙️ Configurações</h1>", unsafe_allow_html=True)
    
    user = st.session_state.user
    st.markdown(f"""<div class='card-info'>
        <b>👤 Informações da Conta</b><br>
        📛 Nome: {user['nome']}<br>
        🎓 Turma: {user['turma']}<br>
        📧 E-mail: {user.get('email', 'N/A')}
    </div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🔒 Alterar Senha")
    
    with st.form("form_alterar_senha"):
        senha_atual = st.text_input("🔐 Senha Atual", type="password")
        senha_nova = st.text_input("🔒 Nova Senha", type="password")
        senha_conf = st.text_input("🔒 Confirme", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("✅ Alterar", use_container_width=True)
        with col2:
            voltar = st.form_submit_button("🔙 Voltar", use_container_width=True)
    
    if submit:
        if not senha_atual or not senha_nova:
            st.error("❌ Preencha tudo!")
        elif senha_nova != senha_conf:
            st.error("❌ Senhas não coincidem!")
        else:
            sucesso, msg = alterar_senha(user['id'], senha_atual, senha_nova)
            if sucesso:
                st.success(f"✅ {msg}")
                st.balloons()
            else:
                st.error(f"❌ {msg}")
    
    if voltar:
        st.session_state.screen = 'dashboard'
        st.rerun()

def cupons_screen():
    st.markdown("<h1 style='color: #22c55e;'>🎁 Cupons</h1>", unsafe_allow_html=True)
    st.session_state.user = buscar_usuario_por_id(st.session_state.user['id'])
    st.markdown(f"### Seus Pontos: {st.session_state.user['pontos']:.1f}")
    
    for cat_nome, cupons in CATEGORIAS.items():
        st.markdown(f"### {cat_nome}")
        for cupom in cupons:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"<div class='card-info'><b>{cupom['nome']}</b> - {cupom['pontos']} pts</div>", unsafe_allow_html=True)
            with col2:
                if st.button("Comprar", key=f"c_{cat_nome}", use_container_width=True):
                    if st.session_state.user['pontos'] < cupom['pontos']:
                        st.error("❌ Pontos insuficientes!")
                    else:
                        atualizar_pontos(st.session_state.user['id'], -cupom['pontos'])
                        codigo = f"CUP-{random.randint(1000, 9999)}"
                        criar_resgate(st.session_state.user['id'], cat_nome, cupom['nome'], codigo, cupom['pontos'])
                        st.success(f"✅ Cupom {codigo}!")
                        st.rerun()
    
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.screen = 'dashboard'
        st.rerun()

def resgates_screen():
    st.markdown("<h1 style='color: #22c55e;'>🎫 Meus Cupons</h1>", unsafe_allow_html=True)
    resgates = [r for r in load_resgates() if r['usuarioId'] == st.session_state.user['id']]
    
    if resgates:
        for r in resgates:
            st.markdown(f"<div class='card-ok'><b>{r['categoria']}</b> - {r['codigo']}</div>", unsafe_allow_html=True)
    else:
        st.info("Nenhum cupom")
    
    if st.button("Voltar", use_container_width=True):
        st.session_state.screen = 'dashboard'
        st.rerun()

def cadastrar_eletro_screen():
    st.markdown("<h1 style='color: #22c55e;'>♻️ Cadastrar</h1>", unsafe_allow_html=True)
    
    linha = st.selectbox("Linha", ['Selecione...'] + list(MATERIAIS.keys()))
    if linha != 'Selecione...':
        materiais = MATERIAIS[linha]
        material_sel = st.selectbox("Material", list(materiais.keys()))
        qtd = st.number_input("Quantidade", min_value=1, value=1)
        pts = materiais[material_sel] * qtd
        
        if st.button("Cadastrar", use_container_width=True, type="primary"):
            numero = f"DSC-{int(datetime.now().timestamp() * 1000)}"
            criar_descarte(st.session_state.user['id'], numero, linha, material_sel, qtd, pts)
            st.success(f"✅ {pts} pts!")
            st.session_state.screen = 'dashboard'
            st.rerun()
        
        if st.button("Voltar", use_container_width=True):
            st.session_state.screen = 'dashboard'
            st.rerun()

def admin_login_screen():
    st.markdown("<h1 style='color: #22c55e;'>🔒 Admin</h1>", unsafe_allow_html=True)
    senha = st.text_input("Senha", type="password")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Entrar", use_container_width=True):
            if senha == ADMIN_PASSWORD:
                st.session_state.screen = 'admin'
                st.rerun()
            else:
                st.error("❌ Incorreto!")
    with col2:
        if st.button("Voltar", use_container_width=True):
            st.session_state.screen = 'home'
            st.rerun()

def admin_screen():
    st.markdown("<h1 style='color: #22c55e;'>⚙️ Admin</h1>", unsafe_allow_html=True)
    
    if st.button("🚪 Sair"):
        st.session_state.screen = 'home'
        st.rerun()
    
    usuarios = load_usuarios()
    descartes = load_descartes()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='stat-card'><p>Usuários</p><h1>{len(usuarios)}</h1></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='stat-card'><p>Descartes</p><h1>{len(descartes)}</h1></div>", unsafe_allow_html=True)
    with col3:
        aprovados = len([d for d in descartes if d['status'] == 'Aprovado'])
        st.markdown(f"<div class='stat-card'><p>Aprovados</p><h1>{aprovados}</h1></div>", unsafe_allow_html=True)

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
