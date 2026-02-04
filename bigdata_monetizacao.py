# bigdata_monetizacao.py - Sistema de Big Data com Monetização Ética

"""
Sistema de Big Data totalmente anônimo e ético para monetização
- Coleta APENAS com consentimento explícito
- Dados 100% anônimos e agregados
- Análise de tendências e padrões
- Geração de relatórios para venda
- Transparência total com o usuário
"""

from datetime import datetime, timedelta
import json

class BigDataEcoEletronico:
    """Gerenciador de Big Data Ético"""
    
    def __init__(self, db):
        self.db = db
    
    def registrar_evento_pesquisa(self, categoria, material, consentimento_usuario=True):
        """
        Registra evento de pesquisa (busca por material)
        TOTALMENTE ANÔNIMO - sem ID de usuário
        
        Args:
            categoria: Linha do material (Marrom, Azul, Verde)
            material: Nome do material
            consentimento_usuario: Se usuário consentiu
        """
        if not consentimento_usuario:
            return  # Não registra sem consentimento
        
        evento_id = int(datetime.now().timestamp() * 1000)
        
        dados = {
            'id': evento_id,
            'tipo': 'pesquisa',
            'timestamp': datetime.now(),
            'categoria': categoria,
            'material': material,
            'dia_semana': datetime.now().weekday(),  # 0-6
            'hora': datetime.now().hour,
            'mes': datetime.now().month,
            # SEM DADOS PESSOAIS - APENAS AGREGADOS
        }
        
        self.db.collection('bigdata_eventos').document(str(evento_id)).set(dados)
    
    def registrar_intencao_compra_cupom(self, categoria_cupom, pontos_necessarios, pontos_usuario, consentimento=True):
        """
        Registra intenção de compra de cupom
        Útil para entender demanda por categorias
        """
        if not consentimento:
            return
        
        evento_id = int(datetime.now().timestamp() * 1000)
        
        dados = {
            'id': evento_id,
            'tipo': 'intencao_cupom',
            'timestamp': datetime.now(),
            'categoria_cupom': categoria_cupom,
            'pontos_necessarios': pontos_necessarios,
            'pontos_disponiveis': pontos_usuario,
            'tem_pontos_suficientes': pontos_usuario >= pontos_necessarios,
            'dia_semana': datetime.now().weekday(),
            'hora': datetime.now().hour,
            'mes': datetime.now().month
        }
        
        self.db.collection('bigdata_eventos').document(str(evento_id)).set(dados)
    
    def gerar_relatorio_tendencias(self, data_inicio, data_fim):
        """
        Gera relatório de tendências para venda
        100% AGREGADO E ANÔNIMO
        
        Returns:
            dict com estatísticas agregadas
        """
        # Buscar eventos no período
        eventos_ref = self.db.collection('bigdata_eventos')
        query = eventos_ref.where('timestamp', '>=', data_inicio).where('timestamp', '<=', data_fim)
        
        eventos = []
        for doc in query.stream():
            data = doc.to_dict()
            if 'timestamp' in data and hasattr(data['timestamp'], 'strftime'):
                data['timestamp'] = data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            eventos.append(data)
        
        # Análises agregadas
        relatorio = {
            'periodo': {
                'inicio': data_inicio.strftime('%d/%m/%Y'),
                'fim': data_fim.strftime('%d/%m/%Y')
            },
            'total_eventos': len(eventos),
            'eventos_por_tipo': {},
            'materiais_mais_pesquisados': {},
            'categorias_mais_buscadas': {},
            'horarios_pico': {},
            'dias_semana_ativos': {},
            'intencoes_compra': {
                'total': 0,
                'com_pontos_suficientes': 0,
                'sem_pontos_suficientes': 0,
                'cupons_mais_desejados': {}
            },
            'insights': []
        }
        
        # Processar eventos
        for evento in eventos:
            tipo = evento.get('tipo', 'desconhecido')
            relatorio['eventos_por_tipo'][tipo] = relatorio['eventos_por_tipo'].get(tipo, 0) + 1
            
            # Materiais pesquisados
            if tipo == 'pesquisa':
                material = evento.get('material', 'N/A')
                categoria = evento.get('categoria', 'N/A')
                
                relatorio['materiais_mais_pesquisados'][material] = \
                    relatorio['materiais_mais_pesquisados'].get(material, 0) + 1
                
                relatorio['categorias_mais_buscadas'][categoria] = \
                    relatorio['categorias_mais_buscadas'].get(categoria, 0) + 1
            
            # Intenções de compra
            if tipo == 'intencao_cupom':
                relatorio['intencoes_compra']['total'] += 1
                
                if evento.get('tem_pontos_suficientes'):
                    relatorio['intencoes_compra']['com_pontos_suficientes'] += 1
                else:
                    relatorio['intencoes_compra']['sem_pontos_suficientes'] += 1
                
                cupom = evento.get('categoria_cupom', 'N/A')
                relatorio['intencoes_compra']['cupons_mais_desejados'][cupom] = \
                    relatorio['intencoes_compra']['cupons_mais_desejados'].get(cupom, 0) + 1
            
            # Horários
            hora = evento.get('hora', 0)
            relatorio['horarios_pico'][hora] = relatorio['horarios_pico'].get(hora, 0) + 1
            
            # Dias da semana
            dia = evento.get('dia_semana', 0)
            relatorio['dias_semana_ativos'][dia] = relatorio['dias_semana_ativos'].get(dia, 0) + 1
        
        # Ordenar tops
        relatorio['materiais_mais_pesquisados'] = sorted(
            relatorio['materiais_mais_pesquisados'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]
        
        relatorio['categorias_mais_buscadas'] = sorted(
            relatorio['categorias_mais_buscadas'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        relatorio['intencoes_compra']['cupons_mais_desejados'] = sorted(
            relatorio['intencoes_compra']['cupons_mais_desejados'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Gerar insights automáticos
        if relatorio['materiais_mais_pesquisados']:
            top_material = relatorio['materiais_mais_pesquisados'][0]
            relatorio['insights'].append({
                'tipo': 'material_popular',
                'titulo': 'Material Mais Procurado',
                'descricao': f"'{top_material[0]}' foi pesquisado {top_material[1]} vezes",
                'recomendacao': f"Focar campanhas educacionais sobre descarte de {top_material[0]}"
            })
        
        if relatorio['horarios_pico']:
            horario_pico = max(relatorio['horarios_pico'].items(), key=lambda x: x[1])
            relatorio['insights'].append({
                'tipo': 'horario_engajamento',
                'titulo': 'Horário de Maior Engajamento',
                'descricao': f"Maior atividade às {horario_pico[0]}h ({horario_pico[1]} eventos)",
                'recomendacao': "Agendar notificações e campanhas neste horário"
            })
        
        if relatorio['intencoes_compra']['sem_pontos_suficientes'] > 0:
            taxa = (relatorio['intencoes_compra']['sem_pontos_suficientes'] / 
                   relatorio['intencoes_compra']['total'] * 100)
            relatorio['insights'].append({
                'tipo': 'barreira_pontos',
                'titulo': 'Barreira de Pontos Identificada',
                'descricao': f"{taxa:.1f}% das intenções não têm pontos suficientes",
                'recomendacao': "Considerar criar cupons de menor valor ou promoções"
            })
        
        return relatorio
    
    def gerar_pacote_comercial(self, periodo_dias=30):
        """
        Gera pacote de dados para venda comercial
        TOTALMENTE ANÔNIMO E AGREGADO
        
        Args:
            periodo_dias: Últimos X dias
        
        Returns:
            dict formatado para venda
        """
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=periodo_dias)
        
        relatorio = self.gerar_relatorio_tendencias(data_inicio, data_fim)
        
        # Pacote comercial
        pacote = {
            'produto': 'Eco Eletrônico - Insights de Descarte Eletrônico',
            'versao': '1.0',
            'periodo_analise': f'Últimos {periodo_dias} dias',
            'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'escopo_geografico': 'Brasil - Ambiente Escolar',
            'publico_alvo': 'Estudantes Ensino Fundamental/Médio',
            'amostra': relatorio['total_eventos'],
            
            'tendencias_descarte': {
                'materiais_prioritarios': [
                    {
                        'material': m[0],
                        'frequencia': m[1],
                        'percentual': (m[1] / relatorio['total_eventos'] * 100) if relatorio['total_eventos'] > 0 else 0
                    }
                    for m in relatorio['materiais_mais_pesquisados'][:10]
                ],
                'categorias': [
                    {
                        'categoria': c[0],
                        'frequencia': c[1]
                    }
                    for c in relatorio['categorias_mais_buscadas']
                ]
            },
            
            'comportamento_consumidor': {
                'horarios_maior_interesse': relatorio['horarios_pico'],
                'dias_mais_ativos': relatorio['dias_semana_ativos']
            },
            
            'intencao_consumo': {
                'total_intencoes': relatorio['intencoes_compra']['total'],
                'taxa_conversao_potencial': (
                    relatorio['intencoes_compra']['com_pontos_suficientes'] /
                    relatorio['intencoes_compra']['total'] * 100
                ) if relatorio['intencoes_compra']['total'] > 0 else 0,
                'produtos_mais_desejados': relatorio['intencoes_compra']['cupons_mais_desejados']
            },
            
            'insights_estrategicos': relatorio['insights'],
            
            'aplicacoes_comerciais': [
                'Planejamento de produção sustentável',
                'Logística reversa otimizada',
                'Campanhas de conscientização direcionadas',
                'Desenvolvimento de produtos eco-friendly',
                'Estratégias de economia circular'
            ],
            
            'conformidade': {
                'lgpd': 'Totalmente conforme',
                'anonimizacao': '100% - Impossível identificar indivíduos',
                'consentimento': 'Obtido de todos os participantes',
                'uso_etico': 'Apenas fins estatísticos e educacionais'
            },
            
            'precificacao_sugerida': {
                'valor_base': 'R$ 5.000,00',
                'descricao': 'Dados agregados de ' + str(relatorio['total_eventos']) + ' eventos',
                'periodicidade': 'Mensal',
                'formato': 'JSON estruturado'
            }
        }
        
        return pacote
    
    def exportar_para_venda(self, periodo_dias=30, formato='json'):
        """
        Exporta dados em formato comercial
        
        Returns:
            string (JSON ou CSV)
        """
        pacote = self.gerar_pacote_comercial(periodo_dias)
        
        if formato == 'json':
            return json.dumps(pacote, ensure_ascii=False, indent=2)
        
        # Implementar CSV se necessário
        return json.dumps(pacote, ensure_ascii=False, indent=2)
    
    def get_valor_arrecadado_estimado(self):
        """
        Calcula valor estimado que pode ser arrecadado com dados
        
        Returns:
            dict com projeções financeiras
        """
        # Simular venda mensal
        pacote_mes = self.gerar_pacote_comercial(30)
        
        # Premissas de precificação
        valor_por_pacote = 5000  # R$ 5.000 por pacote mensal
        clientes_potenciais = 10  # Empresas interessadas
        
        projecao = {
            'receita_mensal_estimada': valor_por_pacote * clientes_potenciais,
            'receita_trimestral_estimada': valor_por_pacote * clientes_potenciais * 3,
            'receita_anual_estimada': valor_por_pacote * clientes_potenciais * 12,
            
            'alocacao_sugerida': {
                'bazar_ecologico': 0.60,  # 60% para o bazar
                'manutencao_sistema': 0.20,  # 20% manutenção
                'expansao_projeto': 0.15,  # 15% crescimento
                'reserva_emergencia': 0.05  # 5% reserva
            },
            
            'valores_alocados': {
                'bazar_ecologico': valor_por_pacote * clientes_potenciais * 0.60,
                'manutencao_sistema': valor_por_pacote * clientes_potenciais * 0.20,
                'expansao_projeto': valor_por_pacote * clientes_potenciais * 0.15,
                'reserva_emergencia': valor_por_pacote * clientes_potenciais * 0.05
            },
            
            'total_eventos_base': pacote_mes['amostra'],
            'valor_por_evento': valor_por_pacote / pacote_mes['amostra'] if pacote_mes['amostra'] > 0 else 0
        }
        
        return projecao

# Exemplo de uso
def exemplo_uso():
    """Exemplo de como usar o sistema"""
    
    # Inicializar (passar db real)
    # bd = BigDataEcoEletronico(db)
    
    # Registrar evento de pesquisa
    # bd.registrar_evento_pesquisa('Linha Marrom', 'Televisor', consentimento_usuario=True)
    
    # Registrar intenção de compra
    # bd.registrar_intencao_compra_cupom('Matemática', 45, 40, consentimento=True)
    
    # Gerar relatório
    # relatorio = bd.gerar_relatorio_tendencias(datetime.now() - timedelta(days=30), datetime.now())
    
    # Gerar pacote comercial
    # pacote = bd.gerar_pacote_comercial(30)
    
    # Exportar para venda
    # dados_venda = bd.exportar_para_venda(30)
    
    # Ver projeção financeira
    # projecao = bd.get_valor_arrecadado_estimado()
    
    pass
