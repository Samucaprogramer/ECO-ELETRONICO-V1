# database_impacto.py - Base de Dados de Impacto Ambiental

"""
Base de dados com informações sobre metais pesados e impacto ambiental
de cada material eletrônico
"""

IMPACTO_AMBIENTAL = {
    'Televisor': {
        'peso_medio_kg': 15.0,
        'metais_pesados': {
            'chumbo': 0.8,      # kg
            'mercurio': 0.002,   # kg
            'cadmio': 0.05,      # kg
            'niquel': 0.15       # kg
        },
        'co2_evitado_kg': 75.0,
        'energia_economizada_kwh': 120.0,
        'agua_economizada_litros': 1500.0,
        'recursos_naturais': ['Cobre', 'Vidro', 'Plástico', 'Metais raros'],
        'danos_descarte_incorreto': [
            '☠️ Chumbo pode contaminar o solo por até 300 anos',
            '🌊 Mercúrio contamina lençóis freáticos',
            '🫁 Cádmio causa problemas respiratórios graves',
            '🧠 Metais pesados afetam desenvolvimento neurológico'
        ],
        'beneficios_descarte_correto': [
            '♻️ Reciclagem de vidro economiza 30% de energia',
            '🔋 Recuperação de cobre reduz mineração',
            '🌱 Evita contaminação de 10.000 litros de água',
            '⚡ Economia de energia equivalente a 2 meses de uma geladeira'
        ]
    },
    'Computador': {
        'peso_medio_kg': 8.0,
        'metais_pesados': {
            'chumbo': 0.5,
            'mercurio': 0.001,
            'cadmio': 0.03,
            'niquel': 0.1
        },
        'co2_evitado_kg': 50.0,
        'energia_economizada_kwh': 80.0,
        'agua_economizada_litros': 1000.0,
        'recursos_naturais': ['Ouro', 'Prata', 'Cobre', 'Platina', 'Alumínio'],
        'danos_descarte_incorreto': [
            '☠️ 1kg de placas eletrônicas pode contaminar 1 milhão de litros de água',
            '🌊 Metais pesados infiltram no solo e água subterrânea',
            '🦴 Chumbo causa danos renais irreversíveis',
            '👶 Afeta desenvolvimento de crianças e fetos'
        ],
        'beneficios_descarte_correto': [
            '♻️ 1 tonelada de PCs = 17kg de cobre, 0.5kg de prata, 0.25kg de ouro',
            '🌱 Evita extração de 1.500kg de minério',
            '⚡ Economia equivalente a 100 recargas de celular',
            '🌍 Reduz emissão de gases de efeito estufa'
        ]
    },
    'Notebook': {
        'peso_medio_kg': 2.5,
        'metais_pesados': {
            'chumbo': 0.15,
            'mercurio': 0.0005,
            'cadmio': 0.01,
            'niquel': 0.05
        },
        'co2_evitado_kg': 25.0,
        'energia_economizada_kwh': 40.0,
        'agua_economizada_litros': 500.0,
        'recursos_naturais': ['Lítio', 'Cobalto', 'Terras raras', 'Alumínio'],
        'danos_descarte_incorreto': [
            '🔋 Baterias de lítio podem causar incêndios em aterros',
            '☠️ Cobalto é altamente tóxico para organismos aquáticos',
            '🌊 Contamina água por gerações',
            '⚠️ Gases tóxicos liberados na decomposição'
        ],
        'beneficios_descarte_correto': [
            '♻️ Recuperação de metais valiosos das baterias',
            '🌱 Reduz mineração de lítio em 70%',
            '⚡ Economia de energia de 1 mês de uso',
            '🌍 Previne contaminação de ecossistemas aquáticos'
        ]
    },
    'Monitor': {
        'peso_medio_kg': 5.0,
        'metais_pesados': {
            'chumbo': 0.3,
            'mercurio': 0.001,
            'cadmio': 0.02,
            'niquel': 0.08
        },
        'co2_evitado_kg': 30.0,
        'energia_economizada_kwh': 50.0,
        'agua_economizada_litros': 700.0,
        'recursos_naturais': ['Vidro', 'Plástico', 'Metais raros'],
        'danos_descarte_incorreto': [
            '👁️ Chumbo em monitores CRT causa danos à visão',
            '☠️ Fósforo libera substâncias cancerígenas',
            '🌊 Contamina fontes de água potável',
            '🧬 Altera DNA de organismos vivos'
        ],
        'beneficios_descarte_correto': [
            '♻️ Vidro pode ser 100% reciclado infinitamente',
            '⚡ Economia de energia significativa na produção',
            '🌱 Previne contaminação de 5.000 litros de água',
            '🌍 Reduz necessidade de extração de areia'
        ]
    },
    'Celular': {
        'peso_medio_kg': 0.15,
        'metais_pesados': {
            'chumbo': 0.005,
            'mercurio': 0.0001,
            'cadmio': 0.002,
            'niquel': 0.01
        },
        'co2_evitado_kg': 10.0,
        'energia_economizada_kwh': 15.0,
        'agua_economizada_litros': 200.0,
        'recursos_naturais': ['Ouro', 'Prata', 'Cobre', 'Paládio', 'Terras raras'],
        'danos_descarte_incorreto': [
            '📱 40 celulares descartados = 1g de ouro perdido',
            '☠️ Lítio das baterias contamina solo por décadas',
            '🌊 Metais pesados chegam à cadeia alimentar',
            '⚠️ Radiação de baterias danificadas'
        ],
        'beneficios_descarte_correto': [
            '♻️ 1 tonelada de celulares = 350g de ouro!',
            '💎 Mais ouro que em minas tradicionais',
            '🌱 Evita mineração predatória',
            '⚡ Recuperação de metais preciosos'
        ]
    },
    'Liquidificador': {
        'peso_medio_kg': 1.5,
        'metais_pesados': {
            'chumbo': 0.05,
            'mercurio': 0.0002,
            'cadmio': 0.005,
            'niquel': 0.02
        },
        'co2_evitado_kg': 8.0,
        'energia_economizada_kwh': 12.0,
        'agua_economizada_litros': 150.0,
        'recursos_naturais': ['Cobre', 'Alumínio', 'Plástico'],
        'danos_descarte_incorreto': [
            '⚡ Fios de cobre liberam substâncias tóxicas',
            '☠️ Motor contém metais pesados',
            '🌊 Plástico não biodegradável',
            '🔥 Risco de combustão em aterros'
        ],
        'beneficios_descarte_correto': [
            '♻️ Alumínio 100% reciclável',
            '⚡ Cobre recuperado reduz mineração',
            '🌱 Economia de 95% de energia na reciclagem',
            '🌍 Reduz volume em aterros sanitários'
        ]
    },
    'Ferro de Passar': {
        'peso_medio_kg': 1.2,
        'metais_pesados': {
            'chumbo': 0.04,
            'mercurio': 0.0001,
            'cadmio': 0.003,
            'niquel': 0.015
        },
        'co2_evitado_kg': 6.0,
        'energia_economizada_kwh': 10.0,
        'agua_economizada_litros': 120.0,
        'recursos_naturais': ['Ferro', 'Alumínio', 'Cobre'],
        'danos_descarte_incorreto': [
            '🔥 Resistências contêm materiais tóxicos',
            '☠️ Revestimentos liberam gases nocivos',
            '🌊 Metais oxidam e contaminam água',
            '⚠️ Componentes elétricos perigosos'
        ],
        'beneficios_descarte_correto': [
            '♻️ Metais ferrosos totalmente recicláveis',
            '⚡ Grande economia energética',
            '🌱 Reduz extração de minério de ferro',
            '🌍 Menos poluição atmosférica'
        ]
    },
    'Ventilador': {
        'peso_medio_kg': 2.5,
        'metais_pesados': {
            'chumbo': 0.1,
            'mercurio': 0.0003,
            'cadmio': 0.01,
            'niquel': 0.03
        },
        'co2_evitado_kg': 12.0,
        'energia_economizada_kwh': 18.0,
        'agua_economizada_litros': 250.0,
        'recursos_naturais': ['Cobre', 'Aço', 'Alumínio', 'Plástico'],
        'danos_descarte_incorreto': [
            '⚡ Motor elétrico contém metais pesados',
            '☠️ Fios de cobre oxidam e contaminam',
            '🌊 Componentes não biodegradáveis',
            '🔥 Risco de curto-circuito em aterros'
        ],
        'beneficios_descarte_correto': [
            '♻️ Motores elétricos são 90% recicláveis',
            '⚡ Cobre recuperado vale muito',
            '🌱 Evita extração de novos recursos',
            '🌍 Reduz pegada de carbono industrial'
        ]
    },
    'Bateria': {
        'peso_medio_kg': 0.05,
        'metais_pesados': {
            'chumbo': 0.01,
            'mercurio': 0.0005,
            'cadmio': 0.008,
            'niquel': 0.015
        },
        'co2_evitado_kg': 5.0,
        'energia_economizada_kwh': 8.0,
        'agua_economizada_litros': 100.0,
        'recursos_naturais': ['Lítio', 'Níquel', 'Cobalto', 'Manganês'],
        'danos_descarte_incorreto': [
            '☠️ UMA PILHA contamina 200.000 litros de água!',
            '🌊 Mercúrio bioacumula em peixes',
            '🐟 Cadmio mata vida aquática',
            '⚠️ Risco de explosão e incêndio'
        ],
        'beneficios_descarte_correto': [
            '♻️ 100% dos materiais são recuperáveis',
            '🔋 Lítio reciclado para novas baterias',
            '🌱 Previne desastre ambiental',
            '⚡ Economia circular de materiais valiosos'
        ]
    },
    'Carregador': {
        'peso_medio_kg': 0.1,
        'metais_pesados': {
            'chumbo': 0.003,
            'mercurio': 0.0001,
            'cadmio': 0.001,
            'niquel': 0.005
        },
        'co2_evitado_kg': 3.0,
        'energia_economizada_kwh': 5.0,
        'agua_economizada_litros': 80.0,
        'recursos_naturais': ['Cobre', 'Plástico', 'Silício'],
        'danos_descarte_incorreto': [
            '⚡ Circuitos eletrônicos liberam toxinas',
            '☠️ Plástico não biodegradável',
            '🌊 Metais infiltram no solo',
            '🔥 Risco de combustão espontânea'
        ],
        'beneficios_descarte_correto': [
            '♻️ Recuperação de cobre valioso',
            '⚡ Componentes eletrônicos reutilizáveis',
            '🌱 Reduz lixo eletrônico',
            '🌍 Menos extração de recursos'
        ]
    },
    'Fone de Ouvido': {
        'peso_medio_kg': 0.03,
        'metais_pesados': {
            'chumbo': 0.001,
            'mercurio': 0.00005,
            'cadmio': 0.0005,
            'niquel': 0.002
        },
        'co2_evitado_kg': 2.0,
        'energia_economizada_kwh': 3.0,
        'agua_economizada_litros': 50.0,
        'recursos_naturais': ['Cobre', 'Plástico', 'Borracha'],
        'danos_descarte_incorreto': [
            '☠️ Fios contêm metais pesados',
            '🌊 Plástico persiste por séculos',
            '⚠️ Micro componentes eletrônicos tóxicos',
            '🐟 Afeta vida marinha'
        ],
        'beneficios_descarte_correto': [
            '♻️ Recuperação de fios de cobre',
            '🌱 Evita acúmulo de micro-lixo',
            '⚡ Plástico pode ser reciclado',
            '🌍 Contribui para economia circular'
        ]
    }
}

def calcular_impacto_total(material, quantidade):
    """
    Calcula o impacto ambiental total do descarte
    
    Args:
        material: Nome do material
        quantidade: Quantidade descartada
    
    Returns:
        dict com todos os impactos calculados
    """
    if material not in IMPACTO_AMBIENTAL:
        return None
    
    dados = IMPACTO_AMBIENTAL[material]
    
    return {
        'material': material,
        'quantidade': quantidade,
        'peso_total_kg': dados['peso_medio_kg'] * quantidade,
        'metais_pesados_total': {
            metal: valor * quantidade 
            for metal, valor in dados['metais_pesados'].items()
        },
        'co2_evitado_kg': dados['co2_evitado_kg'] * quantidade,
        'energia_economizada_kwh': dados['energia_economizada_kwh'] * quantidade,
        'agua_economizada_litros': dados['agua_economizada_litros'] * quantidade,
        'recursos_naturais': dados['recursos_naturais'],
        'danos_descarte_incorreto': dados['danos_descarte_incorreto'],
        'beneficios_descarte_correto': dados['beneficios_descarte_correto']
    }

def formatar_impacto_ambiental(impacto):
    """
    Formata o impacto ambiental para exibição
    
    Args:
        impacto: Dicionário retornado por calcular_impacto_total
    
    Returns:
        str formatado em HTML
    """
    if not impacto:
        return ""
    
    html = f"""
    <div style='background: linear-gradient(135deg, #11998e, #38ef7d); 
                color: white; padding: 25px; border-radius: 15px; margin: 20px 0;'>
        <h2 style='text-align: center; margin-bottom: 20px;'>
            🌍 IMPACTO AMBIENTAL DO SEU DESCARTE
        </h2>
        
        <div style='background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; margin: 10px 0;'>
            <h3>📊 Você evitou:</h3>
            <ul style='font-size: 1.1em; line-height: 1.8;'>
                <li><b>☠️ {impacto['metais_pesados_total']['chumbo']:.3f} kg de CHUMBO</b></li>
                <li><b>☢️ {impacto['metais_pesados_total']['mercurio']:.4f} kg de MERCÚRIO</b></li>
                <li><b>⚠️ {impacto['metais_pesados_total']['cadmio']:.3f} kg de CÁDMIO</b></li>
                <li><b>🔩 {impacto['metais_pesados_total']['niquel']:.3f} kg de NÍQUEL</b></li>
            </ul>
        </div>
        
        <div style='background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; margin: 10px 0;'>
            <h3>✅ Benefícios Ambientais:</h3>
            <ul style='font-size: 1.1em; line-height: 1.8;'>
                <li><b>🌱 {impacto['co2_evitado_kg']:.1f} kg de CO₂ evitado</b></li>
                <li><b>⚡ {impacto['energia_economizada_kwh']:.1f} kWh de energia economizada</b></li>
                <li><b>💧 {impacto['agua_economizada_litros']:.0f} litros de água preservados</b></li>
                <li><b>♻️ {impacto['peso_total_kg']:.2f} kg de material reciclável</b></li>
            </ul>
        </div>
        
        <div style='background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; margin: 10px 0;'>
            <h3>💎 Recursos Naturais Preservados:</h3>
            <p style='font-size: 1.1em;'>{', '.join(impacto['recursos_naturais'])}</p>
        </div>
    </div>
    
    <div style='background: linear-gradient(135deg, #ee0979, #ff6a00); 
                color: white; padding: 20px; border-radius: 15px; margin: 20px 0;'>
        <h3>❌ DANOS SE FOSSE DESCARTADO INCORRETAMENTE:</h3>
        <ul style='font-size: 1.05em; line-height: 1.8;'>
    """
    
    for dano in impacto['danos_descarte_incorreto']:
        html += f"<li>{dano}</li>"
    
    html += """
        </ul>
    </div>
    
    <div style='background: linear-gradient(135deg, #56ab2f, #a8e063); 
                color: white; padding: 20px; border-radius: 15px; margin: 20px 0;'>
        <h3>✅ BENEFÍCIOS DO DESCARTE CORRETO:</h3>
        <ul style='font-size: 1.05em; line-height: 1.8;'>
    """
    
    for beneficio in impacto['beneficios_descarte_correto']:
        html += f"<li>{beneficio}</li>"
    
    html += """
        </ul>
    </div>
    
    <div style='text-align: center; padding: 15px; background: rgba(255,215,0,0.3); 
                border-radius: 10px; margin: 20px 0;'>
        <h2 style='color: #2c3e50;'>🎉 PARABÉNS!</h2>
        <p style='font-size: 1.2em; color: #2c3e50;'>
            <b>Você acabou de fazer uma GRANDE diferença para o planeta! 🌍</b>
        </p>
    </div>
    """
    
    return html
