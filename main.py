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
