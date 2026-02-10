# identificador_materiais.py - Sistema Inteligente de Identificação de Materiais

"""
Sistema que identifica materiais eletrônicos através de palavras-chave
e fornece sugestões quando não consegue identificar com certeza
"""

import re

# Base de dados de palavras-chave para cada material
PALAVRAS_CHAVE_MATERIAIS = {
    'Televisor': {
        'keywords': ['tv', 'televisor', 'televisão', 'tela', 'monitor tv', 'smart tv', 'led', 'lcd', 'plasma'],
        'categoria': 'Linha Marrom',
        'confianca': 0
    },
    'Computador': {
        'keywords': ['computador', 'pc', 'desktop', 'cpu', 'gabinete', 'torre', 'all in one'],
        'categoria': 'Linha Marrom',
        'confianca': 0
    },
    'Notebook': {
        'keywords': ['notebook', 'laptop', 'note', 'chromebook', 'ultrabook', 'macbook'],
        'categoria': 'Linha Marrom',
        'confianca': 0
    },
    'Monitor': {
        'keywords': ['monitor', 'tela computador', 'display', 'screen', 'crt', 'tela pc'],
        'categoria': 'Linha Marrom',
        'confianca': 0
    },
    'Celular': {
        'keywords': ['celular', 'smartphone', 'telefone', 'iphone', 'android', 'mobile', 'samsung', 'motorola'],
        'categoria': 'Linha Verde',
        'confianca': 0
    },
    'Tablet': {
        'keywords': ['tablet', 'ipad', 'galaxy tab', 'tab'],
        'categoria': 'Linha Verde',
        'confianca': 0
    },
    'Liquidificador': {
        'keywords': ['liquidificador', 'mixer', 'blender', 'batedeira'],
        'categoria': 'Linha Branca',
        'confianca': 0
    },
    'Ferro de Passar': {
        'keywords': ['ferro', 'ferro de passar', 'ferro roupa', 'passadeira', 'ferro eletrico'],
        'categoria': 'Linha Branca',
        'confianca': 0
    },
    'Ventilador': {
        'keywords': ['ventilador', 'ventoinha', 'circulador', 'fan', 'ventilador de teto'],
        'categoria': 'Linha Branca',
        'confianca': 0
    },
    'Bateria': {
        'keywords': ['bateria', 'pilha', 'pilhas', 'baterias', 'power bank', 'carregador portatil'],
        'categoria': 'Linha Verde',
        'confianca': 0
    },
    'Carregador': {
        'keywords': ['carregador', 'fonte', 'adaptador', 'cabo usb', 'cabo carregador', 'fonte alimentacao'],
        'categoria': 'Linha Verde',
        'confianca': 0
    },
    'Fone de Ouvido': {
        'keywords': ['fone', 'headphone', 'earphone', 'fone ouvido', 'auricular', 'headset'],
        'categoria': 'Linha Verde',
        'confianca': 0
    },
    'Teclado': {
        'keywords': ['teclado', 'keyboard', 'teclas'],
        'categoria': 'Linha Verde',
        'confianca': 0
    },
    'Mouse': {
        'keywords': ['mouse', 'rato', 'mouse pad'],
        'categoria': 'Linha Verde',
        'confianca': 0
    },
    'Impressora': {
        'keywords': ['impressora', 'printer', 'multifuncional', 'scanner'],
        'categoria': 'Linha Azul',
        'confianca': 0
    },
    'Roteador': {
        'keywords': ['roteador', 'modem', 'router', 'wifi', 'wi-fi', 'internet'],
        'categoria': 'Linha Azul',
        'confianca': 0
    },
    'Caixa de Som': {
        'keywords': ['caixa som', 'speaker', 'alto falante', 'caixinha', 'bluetooth speaker'],
        'categoria': 'Linha Verde',
        'confianca': 0
    },
    'Webcam': {
        'keywords': ['webcam', 'camera web', 'cam', 'camera'],
        'categoria': 'Linha Verde',
        'confianca': 0
    },
    'HD Externo': {
        'keywords': ['hd', 'hd externo', 'disco rigido', 'hard disk', 'ssd', 'pen drive', 'pendrive'],
        'categoria': 'Linha Verde',
        'confianca': 0
    },
    'Controle Remoto': {
        'keywords': ['controle', 'controle remoto', 'remote', 'controle tv'],
        'categoria': 'Linha Verde',
        'confianca': 0
    },
    'DVD/Blu-ray': {
        'keywords': ['dvd', 'blu-ray', 'bluray', 'player', 'dvd player'],
        'categoria': 'Linha Marrom',
        'confianca': 0
    },
    'Video Game': {
        'keywords': ['video game', 'videogame', 'console', 'playstation', 'xbox', 'nintendo', 'ps', 'joystick'],
        'categoria': 'Linha Marrom',
        'confianca': 0
    },
    'Micro-ondas': {
        'keywords': ['microondas', 'micro-ondas', 'micro ondas', 'forno microondas'],
        'categoria': 'Linha Branca',
        'confianca': 0
    },
    'Geladeira': {
        'keywords': ['geladeira', 'refrigerador', 'freezer', 'frigobar'],
        'categoria': 'Linha Branca',
        'confianca': 0
    },
    'Ar Condicionado': {
        'keywords': ['ar condicionado', 'arcondicionado', 'ar-condicionado', 'ac', 'split'],
        'categoria': 'Linha Branca',
        'confianca': 0
    }
}

def normalizar_texto(texto):
    """
    Normaliza texto para comparação
    Remove acentos, converte para minúsculas, remove caracteres especiais
    """
    if not texto:
        return ""
    
    # Converter para minúsculas
    texto = texto.lower().strip()
    
    # Remover acentos
    replacements = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
        'é': 'e', 'ê': 'e',
        'í': 'i',
        'ó': 'o', 'ô': 'o', 'õ': 'o',
        'ú': 'u', 'ü': 'u',
        'ç': 'c'
    }
    
    for old, new in replacements.items():
        texto = texto.replace(old, new)
    
    # Remover caracteres especiais (manter apenas letras, números e espaços)
    texto = re.sub(r'[^a-z0-9\s]', ' ', texto)
    
    # Remover espaços múltiplos
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    return texto

def calcular_similaridade(descricao, keywords):
    """
    Calcula score de similaridade entre descrição e palavras-chave
    
    Returns:
        float entre 0 e 1 (0 = sem match, 1 = match perfeito)
    """
    descricao_norm = normalizar_texto(descricao)
    
    if not descricao_norm:
        return 0.0
    
    palavras_descricao = set(descricao_norm.split())
    matches = 0
    
    for keyword in keywords:
        keyword_norm = normalizar_texto(keyword)
        
        # Match exato
        if keyword_norm == descricao_norm:
            return 1.0
        
        # Match parcial (keyword contida na descrição)
        if keyword_norm in descricao_norm:
            matches += 2  # Peso maior para match de substring
        
        # Match de palavras individuais
        palavras_keyword = set(keyword_norm.split())
        palavras_comuns = palavras_descricao & palavras_keyword
        if palavras_comuns:
            matches += len(palavras_comuns)
    
    # Normalizar score (máximo seria len(keywords) * 2 + len(palavras))
    max_score = len(keywords) * 3
    score = min(matches / max_score, 1.0) if max_score > 0 else 0.0
    
    return score

def identificar_material(descricao_usuario):
    """
    Identifica material baseado na descrição do usuário
    
    Args:
        descricao_usuario: Texto descrevendo o material
    
    Returns:
        dict com:
        - identificado: bool (conseguiu identificar com confiança?)
        - material: str (nome do material identificado)
        - confianca: float (0-1, nível de confiança)
        - categoria: str (Linha Marrom, Branca, etc)
        - sugestoes: list (materiais similares se não identificou)
    """
    if not descricao_usuario or not descricao_usuario.strip():
        return {
            'identificado': False,
            'material': None,
            'confianca': 0.0,
            'categoria': None,
            'sugestoes': []
        }
    
    # Calcular similaridade com cada material
    scores = []
    
    for material, data in PALAVRAS_CHAVE_MATERIAIS.items():
        score = calcular_similaridade(descricao_usuario, data['keywords'])
        scores.append({
            'material': material,
            'score': score,
            'categoria': data['categoria']
        })
    
    # Ordenar por score (maior para menor)
    scores.sort(key=lambda x: x['score'], reverse=True)
    
    melhor_match = scores[0]
    
    # Critérios de identificação:
    # - Score >= 0.7 = Alta confiança (identificado!)
    # - Score >= 0.4 = Média confiança (sugestão principal)
    # - Score < 0.4 = Baixa confiança (não identificado)
    
    THRESHOLD_ALTA = 0.6
    THRESHOLD_MEDIA = 0.3
    
    if melhor_match['score'] >= THRESHOLD_ALTA:
        # IDENTIFICADO com alta confiança!
        return {
            'identificado': True,
            'material': melhor_match['material'],
            'confianca': melhor_match['score'],
            'categoria': melhor_match['categoria'],
            'sugestoes': []
        }
    
    elif melhor_match['score'] >= THRESHOLD_MEDIA:
        # Confiança média - mostrar sugestões
        sugestoes = [s for s in scores[:5] if s['score'] > 0.1]
        
        return {
            'identificado': False,
            'material': None,
            'confianca': melhor_match['score'],
            'categoria': None,
            'sugestoes': sugestoes
        }
    
    else:
        # Baixa confiança - não identificado
        sugestoes = [s for s in scores[:3] if s['score'] > 0.05]
        
        return {
            'identificado': False,
            'material': None,
            'confianca': 0.0,
            'categoria': None,
            'sugestoes': sugestoes
        }

def formatar_resultado_identificacao(resultado):
    """
    Formata resultado da identificação para exibição
    
    Returns:
        tuple (tipo, mensagem_html)
        tipo: 'sucesso', 'sugestao', 'nao_identificado'
    """
    if resultado['identificado']:
        # IDENTIFICADO!
        confianca_pct = resultado['confianca'] * 100
        
        html = f"""
        <div style='background: linear-gradient(135deg, #11998e, #38ef7d); 
                    color: white; padding: 20px; border-radius: 10px; margin: 10px 0;'>
            <h3>✅ Material Identificado!</h3>
            <p style='font-size: 1.2em; margin: 10px 0;'>
                <b>{resultado['material']}</b>
            </p>
            <p style='font-size: 0.9em; opacity: 0.9;'>
                Categoria: {resultado['categoria']}<br>
                Confiança: {confianca_pct:.0f}%
            </p>
        </div>
        """
        
        return 'sucesso', html
    
    elif resultado['sugestoes']:
        # NÃO IDENTIFICADO - Mostrar sugestões
        html = f"""
        <div style='background: linear-gradient(135deg, #f093fb, #f5576c); 
                    color: white; padding: 20px; border-radius: 10px; margin: 10px 0;'>
            <h3>⚠️ Não foi possível identificar o material com certeza</h3>
            <p style='font-size: 1.1em; margin: 10px 0;'>
                O material que você descreveu poderia ser:
            </p>
            <ul style='font-size: 1.05em; line-height: 1.8;'>
        """
        
        for sug in resultado['sugestoes']:
            confianca = sug['score'] * 100
            html += f"<li><b>{sug['material']}</b> ({sug['categoria']}) - {confianca:.0f}% de certeza</li>"
        
        html += """
            </ul>
            <p style='font-size: 0.95em; margin-top: 15px; opacity: 0.95;'>
                💡 <b>Dica:</b> Se nenhuma dessas opções corresponder ao seu material, 
                você pode prosseguir com a descrição que você deu. 
                O descarte será catalogado como "Não Identificado" e será aprovado normalmente!
            </p>
        </div>
        """
        
        return 'sugestao', html
    
    else:
        # NÃO IDENTIFICADO - Sem sugestões
        html = f"""
        <div style='background: linear-gradient(135deg, #667eea, #764ba2); 
                    color: white; padding: 20px; border-radius: 10px; margin: 10px 0;'>
            <h3>ℹ️ Material Não Identificado</h3>
            <p style='font-size: 1.1em; margin: 10px 0;'>
                Não conseguimos identificar automaticamente o material que você descreveu.
            </p>
            <p style='font-size: 1.05em; margin: 10px 0;'>
                <b>Não tem problema!</b> 😊
            </p>
            <p style='font-size: 0.95em; opacity: 0.95;'>
                Seu descarte será registrado com a descrição que você forneceu 
                e será catalogado como <b>"Material Não Identificado"</b>.
                <br><br>
                O processo de aprovação segue normalmente e você receberá seus pontos! ✨
            </p>
        </div>
        """
        
        return 'nao_identificado', html

# Exemplos de uso
def testar_identificador():
    """Testes do sistema"""
    
    testes = [
        "um celular velho",
        "televisão quebrada",
        "notebook dell",
        "carregador de telefone",
        "uma coisa que liga no computador",
        "negocio de passar roupa",
        "caixa de som bluetooth",
        "troço que toca musica",
        "aparelho de fazer vento"
    ]
    
    print("🧪 TESTANDO IDENTIFICADOR DE MATERIAIS\n")
    
    for teste in testes:
        resultado = identificar_material(teste)
        tipo, html = formatar_resultado_identificacao(resultado)
        
        print(f"Descrição: '{teste}'")
        print(f"Tipo: {tipo}")
        print(f"Identificado: {resultado['identificado']}")
        if resultado['identificado']:
            print(f"Material: {resultado['material']}")
        elif resultado['sugestoes']:
            print(f"Sugestões: {[s['material'] for s in resultado['sugestoes']]}")
        print("-" * 60)

if __name__ == "__main__":
    testar_identificador()
