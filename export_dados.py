# export_dados.py
# Sistema de exportação e registro de dados
# Não interfere nas atividades do app

import csv
import io
import json
from datetime import datetime
import streamlit as st

# ========================================
# EXPORTAR DADOS EM CSV
# ========================================

def exportar_usuarios_csv(usuarios):
    """Exporta usuários para CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['ID', 'Nome', 'Turma', 'Email', 'Pontos', 'Data Cadastro', 'Ativo'])
    
    for user in usuarios:
        writer.writerow([
            user.get('id', ''),
            user.get('nome', ''),
            user.get('turma', ''),
            user.get('email', ''),
            user.get('pontos', 0),
            user.get('dataCadastro', ''),
            user.get('ativo', True)
        ])
    
    return output.getvalue()

def exportar_descartes_csv(descartes, usuarios):
    """Exporta descartes para CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['ID', 'Aluno', 'Turma', 'Linha', 'Material', 'Quantidade', 'Pontos', 'Status', 'Data'])
    
    for desc in descartes:
        user = next((u for u in usuarios if u['id'] == desc['usuarioId']), None)
        writer.writerow([
            desc.get('numero', ''),
            user['nome'] if user else 'N/A',
            user['turma'] if user else 'N/A',
            desc.get('linha', ''),
            desc.get('material', ''),
            desc.get('quantidade', 0),
            desc.get('pontos', 0),
            desc.get('status', ''),
            desc.get('data', '')
        ])
    
    return output.getvalue()

def exportar_resgates_csv(resgates, usuarios):
    """Exporta resgates para CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['ID', 'Aluno', 'Turma', 'Categoria', 'Cupom', 'Código', 'Pontos', 'Status', 'Data'])
    
    for resgate in resgates:
        user = next((u for u in usuarios if u['id'] == resgate['usuarioId']), None)
        writer.writerow([
            resgate.get('id', ''),
            user['nome'] if user else 'N/A',
            user['turma'] if user else 'N/A',
            resgate.get('categoria', ''),
            resgate.get('cupom', ''),
            resgate.get('codigo', ''),
            resgate.get('pontos', 0),
            resgate.get('status', ''),
            resgate.get('data', '')
        ])
    
    return output.getvalue()

def exportar_cupons_csv(resgates, usuarios):
    """Exporta cupons para CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Código', 'Aluno', 'Turma', 'Categoria', 'Cupom', 'Pontos', 'Status', 'Data'])
    
    for resgate in resgates:
        user = next((u for u in usuarios if u['id'] == resgate['usuarioId']), None)
        writer.writerow([
            resgate.get('codigo', ''),
            user['nome'] if user else 'N/A',
            user['turma'] if user else 'N/A',
            resgate.get('categoria', ''),
            resgate.get('cupom', ''),
            resgate.get('pontos', 0),
            resgate.get('status', ''),
            resgate.get('data', '')
        ])
    
    return output.getvalue()

def exportar_ranking_csv(usuarios, descartes):
    """Exporta ranking para CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Posição', 'Nome', 'Turma', 'Pontos', 'Descartes Aprovados'])
    
    usuarios_ordenados = sorted(usuarios, key=lambda x: x.get('pontos', 0), reverse=True)
    
    for i, user in enumerate(usuarios_ordenados, 1):
        descartes_user = len([d for d in descartes if d['usuarioId'] == user['id'] and d['status'] == 'Aprovado'])
        writer.writerow([
            i,
            user['nome'],
            user['turma'],
            user.get('pontos', 0),
            descartes_user
        ])
    
    return output.getvalue()

def exportar_relatorio_completo_csv(usuarios, descartes, resgates):
    """Exporta relatório completo com timestamp"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Cabeçalho com data/hora
    data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    writer.writerow(['RELATÓRIO COMPLETO ECO ELETRÔNICO'])
    writer.writerow([f'Data/Hora de Exportação: {data_hora}'])
    writer.writerow([])
    
    # RESUMO
    writer.writerow(['RESUMO'])
    writer.writerow(['Total de Alunos:', len(usuarios)])
    writer.writerow(['Total de Descartes:', len(descartes)])
    writer.writerow(['Descartes Aprovados:', len([d for d in descartes if d['status'] == 'Aprovado'])])
    writer.writerow(['Total de Cupons:', len(resgates)])
    writer.writerow(['Cupons Aprovados:', len([r for r in resgates if r['status'] == 'Aprovado'])])
    writer.writerow([])
    
    # RANKING TOP 10
    writer.writerow(['RANKING TOP 10'])
    writer.writerow(['Posição', 'Nome', 'Turma', 'Pontos', 'Descartes'])
    
    usuarios_ordenados = sorted(usuarios, key=lambda x: x.get('pontos', 0), reverse=True)
    for i, user in enumerate(usuarios_ordenados[:10], 1):
        descartes_user = len([d for d in descartes if d['usuarioId'] == user['id'] and d['status'] == 'Aprovado'])
        writer.writerow([i, user['nome'], user['turma'], user.get('pontos', 0), descartes_user])
    
    writer.writerow([])
    writer.writerow(['TODOS OS DESCARTES'])
    writer.writerow(['ID', 'Aluno', 'Turma', 'Linha', 'Material', 'Quantidade', 'Pontos', 'Status', 'Data'])
    
    for desc in descartes:
        user = next((u for u in usuarios if u['id'] == desc['usuarioId']), None)
        writer.writerow([
            desc.get('numero', ''),
            user['nome'] if user else 'N/A',
            user['turma'] if user else 'N/A',
            desc.get('linha', ''),
            desc.get('material', ''),
            desc.get('quantidade', 0),
            desc.get('pontos', 0),
            desc.get('status', ''),
            desc.get('data', '')
        ])
    
    return output.getvalue()

# ========================================
# REGISTRAR EVENTO (LOG)
# ========================================

def registrar_evento(db, tipo_evento, usuario_id, detalhes):
    """
    Registra um evento no banco de dados com timestamp exato
    
    tipo_evento: 'cadastro_usuario', 'descarte_cadastrado', 'descarte_aprovado', 
                 'cupom_resgatado', 'cupom_aprovado', 'senha_alterada', etc
    usuario_id: ID do usuário que causou o evento
    detalhes: Dicionário com mais informações
    """
    if not db:
        return False
    
    try:
        evento_id = int(datetime.now().timestamp() * 1000)
        
        dados = {
            'id': evento_id,
            'tipo': tipo_evento,
            'usuario_id': usuario_id,
            'timestamp': datetime.now(),
            'timestamp_str': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'detalhes': detalhes
        }
        
        db.collection('log_eventos').document(str(evento_id)).set(dados)
        return True
    except:
        return False

def exportar_log_eventos_csv(db):
    """Exporta log de eventos para CSV"""
    if not db:
        return None
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['ID', 'Tipo', 'Usuário ID', 'Data/Hora', 'Detalhes'])
    
    try:
        docs = db.collection('log_eventos').stream()
        eventos = [doc.to_dict() for doc in docs]
        
        for evento in sorted(eventos, key=lambda x: x.get('timestamp_str', ''), reverse=True):
            writer.writerow([
                evento.get('id', ''),
                evento.get('tipo', ''),
                evento.get('usuario_id', ''),
                evento.get('timestamp_str', ''),
                json.dumps(evento.get('detalhes', {}), ensure_ascii=False)
            ])
        
        return output.getvalue()
    except:
        return None

# ========================================
# INTERFACE DE EXPORT (ADMIN)
# ========================================

def mostrar_painel_export(db, usuarios, descartes, resgates):
    """Mostra painel de exportação de dados no admin"""
    
    st.markdown("---")
    st.markdown("### 💾 Exportar Dados")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📥 Usuários (CSV)", use_container_width=True):
            csv_data = exportar_usuarios_csv(usuarios)
            st.download_button(
                label="⬇️ Baixar Usuários.csv",
                data=csv_data,
                file_name=f"usuarios_{datetime.now().strftime('%d_%m_%Y_%H_%M')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📥 Descartes (CSV)", use_container_width=True):
            csv_data = exportar_descartes_csv(descartes, usuarios)
            st.download_button(
                label="⬇️ Baixar Descartes.csv",
                data=csv_data,
                file_name=f"descartes_{datetime.now().strftime('%d_%m_%Y_%H_%M')}.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("📥 Cupons (CSV)", use_container_width=True):
            csv_data = exportar_cupons_csv(resgates, usuarios)
            st.download_button(
                label="⬇️ Baixar Cupons.csv",
                data=csv_data,
                file_name=f"cupons_{datetime.now().strftime('%d_%m_%Y_%H_%M')}.csv",
                mime="text/csv"
            )
    
    with col4:
        if st.button("📥 Ranking (CSV)", use_container_width=True):
            csv_data = exportar_ranking_csv(usuarios, descartes)
            st.download_button(
                label="⬇️ Baixar Ranking.csv",
                data=csv_data,
                file_name=f"ranking_{datetime.now().strftime('%d_%m_%Y_%H_%M')}.csv",
                mime="text/csv"
            )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 Relatório Completo", use_container_width=True):
            csv_data = exportar_relatorio_completo_csv(usuarios, descartes, resgates)
            st.download_button(
                label="⬇️ Baixar Relatório.csv",
                data=csv_data,
                file_name=f"relatorio_completo_{datetime.now().strftime('%d_%m_%Y_%H_%M')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📜 Log de Eventos", use_container_width=True):
            csv_data = exportar_log_eventos_csv(db)
            if csv_data:
                st.download_button(
                    label="⬇️ Baixar Log.csv",
                    data=csv_data,
                    file_name=f"log_eventos_{datetime.now().strftime('%d_%m_%Y_%H_%M')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ Nenhum evento registrado")

# ========================================
# EXEMPLOS DE USO
# ========================================

"""
Como usar em main.py:

# No início do arquivo:
from export_dados import registrar_evento, mostrar_painel_export

# Quando criar usuário:
registrar_evento(db, 'cadastro_usuario', user_id, {
    'nome': nome,
    'turma': turma,
    'email': email
})

# Quando cadastrar descarte:
registrar_evento(db, 'descarte_cadastrado', usuario_id, {
    'numero': numero,
    'material': material,
    'quantidade': quantidade,
    'pontos': pontos
})

# Quando aprovar descarte:
registrar_evento(db, 'descarte_aprovado', usuario_id, {
    'descarte_id': descarte_id,
    'pontos_adicionados': pontos
})

# Quando aprovar cupom:
registrar_evento(db, 'cupom_aprovado', usuario_id, {
    'cupom_codigo': codigo,
    'cupom_categoria': categoria,
    'pontos': pontos
})

# No painel de admin:
mostrar_painel_export(db, usuarios, descartes, resgates)
"""
