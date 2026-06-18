# INTEGRAÇÃO DE ENVIO DE EMAIL - PASSO A PASSO

## 📧 O que fazer:

### 1. Copiar o arquivo `email_service.py`
Coloque na mesma pasta que `main.py`

### 2. Adicionar no início do `main.py` (após os imports)

```python
# Logo após as outras importações, ANTES da linha:
# from firebase_admin import credentials, firestore

from email_service import enviar_codigo_recuperacao, enviar_confirmacao_senha_alterada
```

Exemplo de como ficará:
```python
import streamlit as st
from datetime import datetime
import random
import json
import re
import bcrypt
import firebase_admin
from firebase_admin import credentials, firestore

# ← ADICIONE AQUI:
from email_service import enviar_codigo_recuperacao, enviar_confirmacao_senha_alterada

# Importar base de dados de impacto ambiental
try:
    from database_impacto import ...
```

---

### 3. Atualizar a função `recuperar_senha()` no main.py

**ENCONTRE ESTA FUNÇÃO:**
```python
def recuperar_senha(email):
    if not db or not validar_email(email):
        return None, "E-mail inválido"
    
    usuarios_ref = db.collection('usuarios')
    query = usuarios_ref.where('email', '==', email.lower()).limit(1)
    results = list(query.stream())
    
    if not results:
        return None, "E-mail não encontrado"
    
    codigo = f"{random.randint(100000, 999999)}"
    user_doc = results[0]
    user_doc.reference.update({
        'codigoRecuperacao': codigo,
        'codigoExpiracao': datetime.now().timestamp() + 900
    })
    
    return codigo, f"Código de recuperação gerado (em produção seria enviado por e-mail)"
```

**SUBSTITUA POR:**
```python
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
    
    # ← ADICIONE ISTO:
    # Tentar enviar email, mas não falhar se email não estiver configurado
    sucesso, msg = enviar_codigo_recuperacao(
        email.lower(),
        codigo,
        user_data.get('nome', 'Usuário')
    )
    
    if sucesso:
        return codigo, msg
    else:
        # Se falhar, ainda retorna o código (para teste local)
        return codigo, f"⚠️ {msg}\n\n**Código:** {codigo} (válido por 15 minutos)"
```

---

### 4. Atualizar a função `resetar_senha_com_codigo()` no main.py

**ENCONTRE ESTA FUNÇÃO:**
```python
def resetar_senha_com_codigo(email, codigo, senha_nova):
    # ... código existente ...
    
    novo_hash = hash_senha(senha_nova)
    user_ref.update({
        'senha': novo_hash,
        'codigoRecuperacao': firestore.DELETE_FIELD,
        'codigoExpiracao': firestore.DELETE_FIELD
    })
    return True, "Senha resetada com sucesso"
```

**SUBSTITUA O FINAL POR:**
```python
def resetar_senha_com_codigo(email, codigo, senha_nova):
    # ... código existente até o update ...
    
    novo_hash = hash_senha(senha_nova)
    user_ref.update({
        'senha': novo_hash,
        'codigoRecuperacao': firestore.DELETE_FIELD,
        'codigoExpiracao': firestore.DELETE_FIELD
    })
    
    # ← ADICIONE ISTO:
    # Enviar email de confirmação
    user_data = user_doc.to_dict()
    enviar_confirmacao_senha_alterada(
        email.lower(),
        user_data.get('nome', 'Usuário')
    )
    
    return True, "✅ Senha resetada com sucesso! Verifique seu email."
```

---

### 5. Também atualizar a função `alterar_senha()` no main.py

**ENCONTRE:**
```python
def alterar_senha(user_id, senha_atual, senha_nova):
    # ... validações ...
    novo_hash = hash_senha(senha_nova)
    user_ref.update({'senha': novo_hash})
    return True, "Senha alterada com sucesso"
```

**SUBSTITUA POR:**
```python
def alterar_senha(user_id, senha_atual, senha_nova):
    # ... validações existentes ...
    novo_hash = hash_senha(senha_nova)
    user_ref.update({'senha': novo_hash})
    
    # ← ADICIONE ISTO:
    # Enviar email de confirmação
    user_data = user_doc.to_dict()
    enviar_confirmacao_senha_alterada(
        user_data.get('email', ''),
        user_data.get('nome', 'Usuário')
    )
    
    return True, "✅ Senha alterada com sucesso! Verifique seu email."
```

---

## 🔧 CONFIGURAR GMAIL

### Passo 1: Criar App Password no Gmail

1. Acesse sua conta Google: https://myaccount.google.com/
2. Vá para "Segurança" (lado esquerdo)
3. Role até "Senhas de app"
4. Selecione:
   - Dispositivo: "Windows Computer" (ou seu SO)
   - App: "E-mail"
5. Clique "Gerar"
6. Google mostrará uma senha de 16 caracteres
7. **Copie esta senha** (é diferente da sua senha normal do Gmail!)

**Exemplo:**
```
sua senha do Gmail: minhaSenha@123
sua app password: abcd efgh ijkl mnop (16 caracteres com espaços)
```

---

### Passo 2: Configurar no LOCAL (.streamlit/secrets.toml)

```toml
[email]
sender_email = "seu-email@gmail.com"
sender_password = "abcd efgh ijkl mnop"
```

**Salve como:** `.streamlit/secrets.toml`

Exemplo completo:
```toml
[firebase]
key = '{"type":"service_account",...}'

[email]
sender_email = "seu-email@gmail.com"
sender_password = "abcd efgh ijkl mnop"
```

---

### Passo 3: Configurar no STREAMLIT CLOUD

No painel Streamlit Cloud, vá para "Advanced Settings" e adicione:

```toml
[email]
sender_email = "seu-email@gmail.com"
sender_password = "abcd efgh ijkl mnop"
```

---

### Passo 4: NÃO FAZER

❌ Usar sua senha normal do Gmail
❌ Compartilhar a app password
❌ Fazer commit do arquivo secrets.toml (adicione ao .gitignore)

---

## ✅ TESTAR LOCALMENTE

### 1. Certifique-se que tem os arquivos:
```
main.py
database_impacto.py
email_service.py
identificador_materiais.py
.streamlit/secrets.toml  (com email configurado)
requirements.txt
```

### 2. Execute:
```bash
streamlit run main.py
```

### 3. Teste o fluxo:
1. Clique "Esqueci minha senha"
2. Digite um email válido
3. **Você receberá um email real** ✅
4. Copie o código
5. Digite a nova senha
6. Pronto! Você receberá email de confirmação

---

## 🎯 O que muda para o usuário

**Antes:**
```
⚠️ Código gerado (em produção seria enviado por e-mail)
Código: 123456
```

**Depois:**
```
✅ Código enviado para seu-email@exemplo.com
(Email chega em segundos!)
```

---

## ⚠️ TROUBLESHOOTING

### ❌ "Erro de autenticação"
```
✅ Solução: Verifique se copiou corretamente a app password
         Remova espaços se necessário
```

### ❌ "Servidor SMTP não respondeu"
```
✅ Solução: Verifique conexão com internet
         Verifique firewall/antivírus
         Teste em outro navegador
```

### ❌ "O email não chega"
```
✅ Solução: Verifique pasta de spam
         Aguarde alguns segundos
         Confirme email no Firestore está correto
```

### ❌ "ModuleNotFoundError: No module named 'email_service'"
```
✅ Solução: Certifique-se que email_service.py está na mesma pasta que main.py
         Execute: pip install -r requirements.txt
```

---

## 📋 CHECKLIST

- [ ] Arquivo `email_service.py` copiado
- [ ] Import adicionado no `main.py`
- [ ] Função `recuperar_senha()` atualizada
- [ ] Função `resetar_senha_com_codigo()` atualizada
- [ ] Função `alterar_senha()` atualizada
- [ ] App password do Gmail gerado
- [ ] `.streamlit/secrets.toml` criado com email
- [ ] Arquivo de secrets não é commitado (.gitignore)
- [ ] Testado localmente
- [ ] Email recebido com sucesso
- [ ] Deployado no Streamlit Cloud
- [ ] Secrets do Cloud configuradas

---

## 🎉 RESULTADO FINAL

✅ Recuperação de senha com email real
✅ Código enviado automaticamente
✅ Email formatado profissionalmente
✅ Confirmação após alterar senha
✅ Segurança total com app password

**Pronto para usar!** 📧
