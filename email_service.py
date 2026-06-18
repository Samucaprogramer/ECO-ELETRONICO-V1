# email_service.py
# Serviço de envio de emails para recuperação de senha
# Usa Gmail SMTP

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
from datetime import datetime

# ========================================
# CONFIGURAÇÃO DE EMAIL (Gmail)
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
        st.warning(f"⚠️ Email não configurado: {e}")
        return None

def enviar_codigo_recuperacao(email_destinatario, codigo, nome_usuario=""):
    """
    Envia email com código de recuperação de senha
    
    Args:
        email_destinatario: Email do usuário
        codigo: Código de 6 dígitos
        nome_usuario: Nome do usuário (opcional)
    
    Returns:
        (sucesso: bool, mensagem: str)
    """
    
    config = get_email_config()
    if not config:
        return False, "⚠️ Serviço de email não configurado. Tente mais tarde."
    
    try:
        # Criar mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "🔐 Código de Recuperação de Senha - Eco Eletrônico"
        msg['From'] = config['sender_email']
        msg['To'] = email_destinatario
        
        # Texto simples
        texto_simples = f"""
Olá {nome_usuario if nome_usuario else 'Usuário'},

Você solicitou a recuperação de senha no Eco Eletrônico.

Seu código de confirmação é: {codigo}

⏰ VALIDADE: 15 minutos

Se você não solicitou essa recuperação, ignore este email.

---
Eco Eletrônico ♻️
Plataforma de Sustentabilidade
"""
        
        # HTML formatado
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
        
        # Anexar partes
        part1 = MIMEText(texto_simples, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Enviar email
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['sender_email'], config['sender_password'])
            server.send_message(msg)
        
        return True, f"✅ Código enviado para {email_destinatario}"
    
    except smtplib.SMTPAuthenticationError:
        return False, "❌ Erro de autenticação. Verifique credenciais de email."
    except smtplib.SMTPException as e:
        return False, f"❌ Erro ao enviar email: {str(e)}"
    except Exception as e:
        return False, f"❌ Erro inesperado: {str(e)}"

def enviar_confirmacao_senha_alterada(email_destinatario, nome_usuario=""):
    """
    Envia email de confirmação após alterar senha
    
    Args:
        email_destinatario: Email do usuário
        nome_usuario: Nome do usuário (opcional)
    
    Returns:
        (sucesso: bool, mensagem: str)
    """
    
    config = get_email_config()
    if not config:
        return False, "⚠️ Serviço de email não configurado."
    
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
                        
                        <p style="color: #666; font-size: 13px; margin-top: 30px;">
                            <strong>Não reconhece essa alteração?</strong><br>
                            Entre em contato com o suporte imediatamente.
                        </p>
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
        return False, f"⚠️ Erro ao enviar confirmação: {str(e)}"
