# bazar_ecologico.py - Sistema do Cupom de Bazar Físico

"""
Sistema SIMPLIFICADO do Bazar Ecológico
- Bazar é FÍSICO (produtos reais na escola)
- Sistema apenas gerencia o CUPOM DE BAZAR
- Cupom custa 50 pontos
- Admin pode liberar/fechar a venda do cupom
- Alunos compram o cupom e usam no bazar físico
"""

from datetime import datetime

# Configuração do cupom
CUSTO_CUPOM_BAZAR = 50

def verificar_cupom_liberado(db):
    """
    Verifica se o cupom de bazar está liberado para compra
    
    Returns:
        (liberado, trimestre_atual, mensagem)
    """
    config_ref = db.collection('config').document('cupom_bazar')
    config_doc = config_ref.get()
    
    if not config_doc.exists:
        # Criar configuração inicial
        config_ref.set({
            'liberado': False,
            'trimestre': 1,
            'dataLiberacao': None
        })
        return False, 1, "Cupom de Bazar ainda não foi liberado pelo administrador"
    
    config = config_doc.to_dict()
    liberado = config.get('liberado', False)
    trimestre = config.get('trimestre', 1)
    
    if not liberado:
        return False, trimestre, "Cupom de Bazar não está disponível no momento"
    
    return True, trimestre, "Cupom de Bazar disponível!"

def liberar_cupom_bazar(db, trimestre):
    """
    Admin libera o cupom de bazar para compra
    
    Args:
        db: Firestore client
        trimestre: Trimestre atual (1, 2 ou 3)
    
    Returns:
        (sucesso, mensagem)
    """
    config_ref = db.collection('config').document('cupom_bazar')
    
    config_ref.set({
        'liberado': True,
        'trimestre': trimestre,
        'dataLiberacao': datetime.now()
    })
    
    return True, f"✅ Cupom de Bazar LIBERADO para o {trimestre}º trimestre!"

def fechar_cupom_bazar(db):
    """
    Admin fecha o cupom de bazar (não pode mais ser comprado)
    
    Returns:
        (sucesso, mensagem)
    """
    config_ref = db.collection('config').document('cupom_bazar')
    config_doc = config_ref.get()
    
    if config_doc.exists:
        config = config_doc.to_dict()
        trimestre = config.get('trimestre', 1)
    else:
        trimestre = 1
    
    config_ref.set({
        'liberado': False,
        'trimestre': trimestre,
        'dataFechamento': datetime.now()
    })
    
    return True, "🔒 Cupom de Bazar FECHADO! Não pode mais ser comprado."

def comprar_cupom_bazar(db, usuario_id):
    """
    Usuário compra Cupom de Bazar (50 pontos)
    
    Returns:
        (sucesso, mensagem, cupom_codigo)
    """
    # Verificar se cupom está liberado
    liberado, trimestre, msg = verificar_cupom_liberado(db)
    
    if not liberado:
        return False, msg, None
    
    # Buscar usuário
    user_ref = db.collection('usuarios').document(str(usuario_id))
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        return False, "Usuário não encontrado", None
    
    user_data = user_doc.to_dict()
    
    # Verificar pontos
    if user_data.get('pontos', 0) < CUSTO_CUPOM_BAZAR:
        return False, f"❌ Pontos insuficientes! Você tem {user_data.get('pontos', 0)}, precisa de {CUSTO_CUPOM_BAZAR}", None
    
    # Gerar código único do cupom
    cupom_codigo = f"BAZAR-T{trimestre}-{int(datetime.now().timestamp() * 1000)}"
    
    # Deduzir pontos
    novos_pontos = user_data['pontos'] - CUSTO_CUPOM_BAZAR
    user_ref.update({'pontos': novos_pontos})
    
    # Registrar cupom no Firestore
    cupom_data = {
        'codigo': cupom_codigo,
        'usuarioId': usuario_id,
        'usuarioNome': user_data['nome'],
        'usuarioTurma': user_data.get('turma', 'N/A'),
        'trimestre': trimestre,
        'pontosGastos': CUSTO_CUPOM_BAZAR,
        'usado': False,
        'dataCompra': datetime.now(),
        'dataUso': None,
        'observacoes': None
    }
    
    db.collection('cupons_bazar').document(cupom_codigo).set(cupom_data)
    
    return True, f"✅ Cupom de Bazar comprado com sucesso!\n\nCódigo: {cupom_codigo}\n\n📍 Apresente este código no Bazar Físico para trocar por produtos!", cupom_codigo

def marcar_cupom_usado(db, cupom_codigo, observacoes=None):
    """
    Marca cupom como usado (admin faz isso no bazar físico)
    
    Args:
        db: Firestore client
        cupom_codigo: Código do cupom
        observacoes: Observações opcionais (ex: "Trocado por picolé")
    
    Returns:
        (sucesso, mensagem)
    """
    cupom_ref = db.collection('cupons_bazar').document(cupom_codigo)
    cupom_doc = cupom_ref.get()
    
    if not cupom_doc.exists:
        return False, "❌ Cupom não encontrado!"
    
    cupom_data = cupom_doc.to_dict()
    
    if cupom_data.get('usado', False):
        data_uso = cupom_data.get('dataUso', 'N/A')
        if hasattr(data_uso, 'strftime'):
            data_uso = data_uso.strftime('%d/%m/%Y %H:%M')
        return False, f"❌ Cupom já foi usado em {data_uso}"
    
    # Marcar como usado
    cupom_ref.update({
        'usado': True,
        'dataUso': datetime.now(),
        'observacoes': observacoes
    })
    
    return True, f"✅ Cupom {cupom_codigo} marcado como USADO!"

def verificar_cupom(db, cupom_codigo):
    """
    Verifica se um cupom é válido
    
    Returns:
        (valido, cupom_data, mensagem)
    """
    cupom_ref = db.collection('cupons_bazar').document(cupom_codigo)
    cupom_doc = cupom_ref.get()
    
    if not cupom_doc.exists:
        return False, None, "❌ Cupom não encontrado!"
    
    cupom_data = cupom_doc.to_dict()
    
    # Converter timestamps
    if 'dataCompra' in cupom_data and hasattr(cupom_data['dataCompra'], 'strftime'):
        cupom_data['dataCompra'] = cupom_data['dataCompra'].strftime('%d/%m/%Y %H:%M')
    if 'dataUso' in cupom_data and cupom_data['dataUso'] and hasattr(cupom_data['dataUso'], 'strftime'):
        cupom_data['dataUso'] = cupom_data['dataUso'].strftime('%d/%m/%Y %H:%M')
    
    if cupom_data.get('usado', False):
        return False, cupom_data, f"❌ Cupom já utilizado em {cupom_data.get('dataUso', 'data desconhecida')}"
    
    return True, cupom_data, f"✅ Cupom VÁLIDO!\n\nAluno: {cupom_data['usuarioNome']} ({cupom_data['usuarioTurma']})\nTrimestre: {cupom_data['trimestre']}º"

def get_meus_cupons(db, usuario_id):
    """
    Busca todos os cupons de um usuário
    
    Returns:
        Lista de cupons
    """
    cupons_ref = db.collection('cupons_bazar')
    query = cupons_ref.where('usuarioId', '==', usuario_id)
    
    cupons = []
    for doc in query.stream():
        data = doc.to_dict()
        
        # Converter timestamps
        if 'dataCompra' in data and hasattr(data['dataCompra'], 'strftime'):
            data['dataCompra'] = data['dataCompra'].strftime('%d/%m/%Y %H:%M')
        if 'dataUso' in data and data['dataUso'] and hasattr(data['dataUso'], 'strftime'):
            data['dataUso'] = data['dataUso'].strftime('%d/%m/%Y %H:%M')
        
        cupons.append(data)
    
    # Ordenar por data de compra (mais recente primeiro)
    cupons = sorted(cupons, key=lambda x: x.get('dataCompra', ''), reverse=True)
    
    return cupons

def get_estatisticas_cupons(db, trimestre=None):
    """
    Obtém estatísticas dos cupons de bazar
    
    Args:
        trimestre: Filtrar por trimestre (opcional)
    
    Returns:
        dict com estatísticas
    """
    cupons_ref = db.collection('cupons_bazar')
    
    if trimestre:
        query = cupons_ref.where('trimestre', '==', trimestre)
    else:
        query = cupons_ref
    
    cupons = list(query.stream())
    
    total_cupons = len(cupons)
    cupons_usados = 0
    cupons_disponiveis = 0
    pontos_arrecadados = 0
    
    for doc in cupons:
        data = doc.to_dict()
        pontos_arrecadados += data.get('pontosGastos', 0)
        
        if data.get('usado', False):
            cupons_usados += 1
        else:
            cupons_disponiveis += 1
    
    stats = {
        'total_cupons': total_cupons,
        'cupons_usados': cupons_usados,
        'cupons_disponiveis': cupons_disponiveis,
        'taxa_uso': (cupons_usados / total_cupons * 100) if total_cupons > 0 else 0,
        'pontos_arrecadados': pontos_arrecadados,
        'trimestre': trimestre if trimestre else 'Todos'
    }
    
    return stats

def get_todos_cupons(db, filtro='todos'):
    """
    Admin: Lista todos os cupons
    
    Args:
        filtro: 'todos', 'usados', 'disponiveis'
    
    Returns:
        Lista de cupons
    """
    cupons_ref = db.collection('cupons_bazar')
    
    cupons = []
    for doc in cupons_ref.stream():
        data = doc.to_dict()
        
        # Converter timestamps
        if 'dataCompra' in data and hasattr(data['dataCompra'], 'strftime'):
            data['dataCompra'] = data['dataCompra'].strftime('%d/%m/%Y %H:%M')
        if 'dataUso' in data and data['dataUso'] and hasattr(data['dataUso'], 'strftime'):
            data['dataUso'] = data['dataUso'].strftime('%d/%m/%Y %H:%M')
        
        # Aplicar filtro
        if filtro == 'usados' and not data.get('usado', False):
            continue
        if filtro == 'disponiveis' and data.get('usado', False):
            continue
        
        cupons.append(data)
    
    # Ordenar por data de compra (mais recente primeiro)
    cupons = sorted(cupons, key=lambda x: x.get('dataCompra', ''), reverse=True)
    
    return cupons
