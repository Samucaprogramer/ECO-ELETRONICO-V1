# main.py - Eco Eletrônico Completo v2.0
# Requisitos: streamlit
# Rode: streamlit run main.py

import streamlit as st
from datetime import datetime
import random
import json
import os

# Arquivos JSON
USERS_FILE = "db_usuarios.json"
DESCARTES_FILE = "db_descartes.json"
RESGATES_FILE = "db_resgates.json"

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_db():
    if 'usuarios' not in st.session_state:
        st.session_state.usuarios = load_json(USERS_FILE)
        st.session_state.descartes = load_json(DESCARTES_FILE)
        st.session_state.resgates = load_json(RESGATES_FILE)

def save_db():
    save_json(USERS_FILE, st.session_state.usuarios)
    save_json(DESCARTES_FILE, st.session_state.descartes)
    save_json(RESGATES_FILE, st.session_state.resgates)

st.set_page_config(page_title="Eco Eletrônico", page_icon="♻️", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .stat-card { background: linear-gradient(135deg, #667eea, #764ba2); color: white; 
                 padding: 30px; border-radius: 15px; text-align: center; margin: 20px 0; }
    .stat-card h1 { font-size: 3em; margin: 10px 0; }
    .card-ok { background: #d4edda; border: 2px solid #28a745; padding: 20px; 
               border-radius: 10px; margin: 15px 0; color: #0b3d13; }
    .card-wait { background: #fff3cd; border: 2px solid #ffc107; padding: 20px; 
                 border-radius: 10px; margin: 15px 0; color: #000; }
    h1 { color: #667eea; text-align: center; }
    .stButton>button { border-radius: 8px; font-weight: 600; padding: 12px 25px; 
                       transition: all 0.3s; color: #000 !important; }
    .stButton>button:hover { transform: translateY(-2px); opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

load_db()

if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.screen = 'home'
    st.session_state.categoria = None
    st.session_state.quiz_completo = False
    st.session_state.classificacao_completo = False
    st.session_state.cruzadinha_completo = False
    st.session_state.jogos_recompensa_recebida = False

TURMAS = ['501', '502', '503', '504', '601', '602', '603', '604', '605', '606',
          '701', '702', '703', '704', '705', '706', '707', '708',
          '801', '802', '803', '804', '805', '806', '807',
          '901', '902', '903', '904', '905']

MATERIAIS = {
    'Linha Marrom': {'Televisor': 5, 'Computador': 4, 'Notebook': 3.5, 'Monitor': 3},
    'Linha Azul': {'Liquidificador': 1.5, 'Ferro de Passar': 1, 'Ventilador': 2},
    'Linha Verde': {'Celular': 2.5, 'Bateria': 1.5, 'Carregador': 1, 'Fone de Ouvido': 0.5}
}

CATEGORIAS = {
    'Direção': [{'nome': 'Brinde', 'pontos': 35}, {'nome': 'Pizza', 'pontos': 50}],
    'Matemática': [{'nome': 'Cupom Matemática', 'pontos': 45}],
    'Português': [{'nome': 'Cupom Português', 'pontos': 45}],
    'Inglês': [{'nome': 'Cupom Inglês', 'pontos': 40}],
    'Ed. Física': [{'nome': 'Cupom Ed. Física', 'pontos': 35}],
    'Artes': [{'nome': 'Cupom Artes', 'pontos': 38}],
    'Geografia': [{'nome': 'Cupom Geografia', 'pontos': 42}],
    'História': [{'nome': 'Cupom História', 'pontos': 48}],
}

ADMIN_PASSWORD = 'soadminpode'

def find_user(nome, turma):
    return next((u for u in st.session_state.usuarios if u['nome'] == nome and u['turma'] == turma), None)

def update_points(user_id, points):
    for u in st.session_state.usuarios:
        if u['id'] == user_id:
            u['pontos'] += points
            if st.session_state.user and st.session_state.user['id'] == user_id:
                st.session_state.user['pontos'] = u['pontos']
            save_db()
            break

def sync_user():
    if st.session_state.user:
        st.session_state.user = next((u for u in st.session_state.usuarios if u['id'] == st.session_state.user['id']), st.session_state.user)

def home_screen():
    st.markdown("<h1>♻️ Eco Eletrônico</h1>", unsafe_allow_html=True)
    st.markdown("""<div style='text-align: center; padding: 40px;'>
        <h2 style='color: #667eea;'>Bem-vindo!</h2>
        <p style='font-size: 1.2em;'>📱 Traga eletrônicos | ⭐ Ganhe pontos | 🎁 Troque por cupons</p>
    </div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 Cadastrar", use_container_width=True):
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
    st.markdown("<h1>♻️ Eco Eletrônico</h1>", unsafe_allow_html=True)
    st.markdown("## 📝 Cadastro")

    nome = st.text_input("Nome Completo")
    turma = st.selectbox("Turma", ['Selecione...'] + TURMAS)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cadastrar", use_container_width=True):
            if not nome.strip() or turma == 'Selecione...':
                st.error("❌ Preencha todos os campos!")
            elif find_user(nome.strip(), turma):
                st.error("❌ Usuário já existe!")
            else:
                user = {'id': int(datetime.now().timestamp() * 1000), 'nome': nome.strip(),
                       'turma': turma, 'pontos': 0.0, 'categoriasCompradas': []}
                st.session_state.usuarios.append(user)
                st.session_state.user = user
                save_db()
                st.session_state.screen = 'dashboard'
                st.rerun()
    with col2:
        if st.button("Voltar", use_container_width=True):
            st.session_state.screen = 'home'
            st.rerun()

def login_screen():
    st.markdown("<h1>♻️ Eco Eletrônico</h1>", unsafe_allow_html=True)
    st.markdown("## 🔑 Login")

    nome = st.text_input("Nome Completo")
    turma = st.selectbox("Turma", ['Selecione...'] + TURMAS)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Entrar", use_container_width=True):
            if not nome.strip() or turma == 'Selecione...':
                st.error("❌ Preencha todos os campos!")
            else:
                user = find_user(nome.strip(), turma)
                if user:
                    st.session_state.user = user
                    st.session_state.screen = 'dashboard'
                    st.rerun()
                else:
                    st.error("❌ Usuário não encontrado!")
    with col2:
        if st.button("Voltar", use_container_width=True):
            st.session_state.screen = 'home'
            st.rerun()

def dashboard_screen():
    st.markdown("<h1>♻️ Eco Eletrônico</h1>", unsafe_allow_html=True)
    sync_user()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("📱 Cadastrar Eletrônico", use_container_width=True):
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
        if st.button("📚 Aprendizagem", use_container_width=True):
            st.session_state.screen = 'aprendizagem'
            st.rerun()
    with col5:
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.user = None
            st.session_state.screen = 'home'
            st.rerun()

    st.markdown(f"## 👋 Olá, {st.session_state.user['nome']}!")
    st.markdown(f"<div class='stat-card'><p>Seus Pontos</p><h1>{st.session_state.user['pontos']:.1f}</h1></div>", unsafe_allow_html=True)

    st.markdown("### 📱 Seus Eletrônicos:")
    descartes = [d for d in st.session_state.descartes if d['usuarioId'] == st.session_state.user['id']][:10]

    if descartes:
        for d in descartes:
            card = 'card-ok' if d['status'] == 'Aprovado' else 'card-wait'
            icon = '✅' if d['status'] == 'Aprovado' else '⏳'
            st.markdown(f"""<div class='{card}'>
                <b>Nº:</b> {d['numero']} | <b>Material:</b> {d['material']} ({d['quantidade']} un)<br>
                <b>Pontos:</b> {d['pontos']} | <b>Status:</b> {icon} {d['status']}<br>
                <small>{d['data']}</small></div>""", unsafe_allow_html=True)
    else:
        st.info("Nenhum eletrônico cadastrado ainda")

def cadastrar_eletro_screen():
    st.markdown("<h1>♻️ Eco Eletrônico</h1>", unsafe_allow_html=True)
    st.markdown("## 📱 Cadastrar Eletrônico")

    st.info("ℹ️ **Se houver dúvidas sobre as linhas de lixo eletrônico, consulte a aba de Aprendizagem**")

    linha = st.selectbox("Linha de Lixo Eletrônico", ['Selecione...'] + list(MATERIAIS.keys()))

    if linha != 'Selecione...':
        materiais = MATERIAIS[linha]
        opcoes_materiais = list(materiais.keys()) + ['📝 Outro material (escrever)']

        material_selecionado = st.selectbox("Material", opcoes_materiais,
                                            format_func=lambda x: f"{x} ({materiais.get(x, '?')}pts)" if x != '📝 Outro material (escrever)' else x)

        # Se escolher "Outro material"
        if material_selecionado == '📝 Outro material (escrever)':
            st.warning("⚠️ **ATENÇÃO:** Não aceitamos materiais de grande porte ou da Linha Branca (geladeiras, fogões, máquinas de lavar, etc.)")

            material_customizado = st.text_input("Digite o nome do material eletrônico:")
            pontos_customizado = st.number_input("Pontos sugeridos (será avaliado pelo administrador):",
                                                 min_value=0.5, max_value=5.0, value=2.0, step=0.5)

            material_final = material_customizado
            pontos_final = pontos_customizado

            if not material_customizado.strip():
                st.error("❌ Por favor, digite o nome do material!")
                material_final = None
        else:
            material_final = material_selecionado
            pontos_final = materiais[material_selecionado]

        qtd = st.number_input("Quantidade", min_value=1, value=1)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cadastrar", use_container_width=True):
                if material_final and material_final.strip():
                    pts = pontos_final * qtd
                    descarte = {
                        'id': int(datetime.now().timestamp() * 1000),
                        'usuarioId': st.session_state.user['id'],
                        'numero': f"DSC-{int(datetime.now().timestamp() * 1000)}",
                        'linha': linha,
                        'material': material_final.strip(),
                        'quantidade': qtd,
                        'pontos': pts,
                        'status': 'Pendente',
                        'customizado': material_selecionado == '📝 Outro material (escrever)',
                        'data': datetime.now().strftime('%d/%m/%Y %H:%M')
                    }
                    st.session_state.descartes.append(descarte)
                    save_db()

                    if material_selecionado == '📝 Outro material (escrever)':
                        st.success(f"✅ Material customizado cadastrado! {pts} pontos sugeridos (aguardando avaliação do administrador)")
                    else:
                        st.success(f"✅ Cadastrado! {pts} pontos (aguardando aprovação)")

                    st.session_state.screen = 'dashboard'
                    st.rerun()
                else:
                    st.error("❌ Preencha o nome do material!")
        with col2:
            if st.button("Voltar", use_container_width=True):
                st.session_state.screen = 'dashboard'
                st.rerun()
    else:
        if st.button("Voltar", use_container_width=True):
            st.session_state.screen = 'dashboard'
            st.rerun()

def cupons_screen():
    st.markdown("<h1>♻️ Eco Eletrônico</h1><h2>🎁 Cupons Disponíveis</h2>", unsafe_allow_html=True)
    sync_user()

    st.markdown(f"### Seus pontos: {st.session_state.user['pontos']:.1f}")

    cats_disponiveis = [c for c in CATEGORIAS.keys() if c == 'Direção' or c not in st.session_state.user.get('categoriasCompradas', [])]

    if st.session_state.categoria:
        cat = st.session_state.categoria
        st.markdown(f"### 🎫 {cat}")

        for cupom in CATEGORIAS[cat]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"<div class='card-wait'><b>{cupom['nome']}</b> - {cupom['pontos']} pts</div>", unsafe_allow_html=True)
            with col2:
                if st.button("Comprar", key=f"comprar_{cat}_{cupom['nome']}", use_container_width=True):
                    if cat != 'Direção' and cat in st.session_state.user.get('categoriasCompradas', []):
                        st.error("❌ Você já comprou dessa categoria!")
                    elif st.session_state.user['pontos'] < cupom['pontos']:
                        st.error("❌ Pontos insuficientes!")
                    else:
                        st.session_state.user['pontos'] -= cupom['pontos']
                        if cat != 'Direção':
                            st.session_state.user.setdefault('categoriasCompradas', []).append(cat)

                        codigo = f"CUP-{random.randint(1000, 9999)}"
                        resgate = {'id': int(datetime.now().timestamp() * 1000), 'usuarioId': st.session_state.user['id'],
                                  'categoria': cat, 'cupom': cupom['nome'], 'codigo': codigo, 'pontos': cupom['pontos'],
                                  'status': 'Pendente', 'data': datetime.now().strftime('%d/%m/%Y %H:%M')}
                        st.session_state.resgates.append(resgate)

                        for i, u in enumerate(st.session_state.usuarios):
                            if u['id'] == st.session_state.user['id']:
                                st.session_state.usuarios[i] = st.session_state.user
                                break
                        save_db()
                        st.success(f"✅ Cupom {codigo} solicitado!")
                        st.session_state.categoria = None
                        st.rerun()

        if st.button("⬅️ Voltar", use_container_width=True):
            st.session_state.categoria = None
            st.rerun()
    else:
        cols = st.columns(3)
        for idx, cat in enumerate(cats_disponiveis):
            with cols[idx % 3]:
                if st.button(cat, use_container_width=True):
                    st.session_state.categoria = cat
                    st.rerun()

    if st.button("🏠 Dashboard", use_container_width=True):
        st.session_state.screen = 'dashboard'
        st.session_state.categoria = None
        st.rerun()

def resgates_screen():
    st.markdown("<h1>♻️ Eco Eletrônico</h1><h2>🎫 Meus Cupons</h2>", unsafe_allow_html=True)

    resgates = [r for r in st.session_state.resgates if r['usuarioId'] == st.session_state.user['id']]

    if resgates:
        for r in resgates:
            if r['status'] == 'Aprovado':
                card, status = 'card-ok', '✅ Aprovado - Você pode usar!'
            elif r['status'] == 'Recusado':
                card, status = 'card-wait', '❌ Recusado'
            else:
                card, status = 'card-wait', '⏳ Aguardando aprovação'

            st.markdown(f"""<div class='{card}'>
                <b>🎫 {r['categoria']} - {r['cupom']}</b><br>
                Código: <b style='font-size:24px'>{r['codigo']}</b><br>
                <b>Pontos:</b> {r['pontos']} | <b>Status:</b> {status}<br>
                <small>{r['data']}</small></div>""", unsafe_allow_html=True)
    else:
        st.info("Nenhum cupom resgatado ainda")

    if st.button("Voltar", use_container_width=True):
        st.session_state.screen = 'dashboard'
        st.rerun()

def aprendizagem_screen():
    st.markdown("<h1>♻️ Eco Eletrônico</h1><h2>📚 Aprendizagem</h2>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📖 O que é", "♻️ As 4 Linhas", "🌍 Impactos"])

    with tab1:
        st.markdown("""
        ### 📖 O que é Lixo Eletrônico?
        
        Lixo eletrônico, também chamado de **e-lixo** ou **REEE** (Resíduos de Equipamentos Eletroeletrônicos), 
        refere-se a todos os equipamentos elétricos e eletrônicos descartados quando não funcionam mais ou 
        foram substituídos por versões mais novas.
        
        Segundo a Organização das Nações Unidas (ONU), em seu relatório "Global E-waste Monitor 2020", 
        o lixo eletrônico é definido como qualquer item com componentes elétricos ou eletrônicos descartado 
        sem intenção de reutilização.
        
        #### 📱 Exemplos Comuns:
        - Celulares e smartphones
        - Computadores e notebooks
        - Monitores e televisores
        - Carregadores e cabos
        - Baterias e pilhas
        - Fones de ouvido
        - Tablets e smartwatches
        
        #### 📊 Dados Globais (Global E-waste Monitor 2020 - ONU):
        - Em 2019, foram geradas **53,6 milhões de toneladas** de lixo eletrônico no mundo
        - Apenas **17,4%** foram coletados e reciclados adequadamente
        - O restante foi descartado incorretamente ou acabou em aterros sanitários
        
        **Fonte:** FORTI, V. et al. The Global E-waste Monitor 2020. United Nations University (UNU), 
        International Telecommunication Union (ITU) & International Solid Waste Association (ISWA), 2020.
        """)

    with tab2:
        st.markdown("""
        ### ♻️ As 4 Linhas de Lixo Eletrônico
        
        A classificação em "linhas" ajuda a organizar o descarte e reciclagem de acordo com 
        características semelhantes dos equipamentos.
        
        #### 🟥 Linha Branca
        **Eletrodomésticos de grande porte**
        
        **Exemplos:** Geladeiras, fogões, micro-ondas, máquinas de lavar, ar-condicionado, freezers
        
        **Por que são perigosos?**
        - Geladeiras e ar-condicionados antigos contêm **gases CFC** (clorofluorcarbonos)
        - Os CFCs destroem a camada de ozônio quando liberados na atmosfera
        - Contêm **metais pesados** como mercúrio em termostatos
        - Óleos lubrificantes dos compressores são **altamente poluentes**
        
        Segundo o Protocolo de Montreal (1987), os CFCs foram banidos por causarem danos irreversíveis 
        à camada de ozônio. A reciclagem adequada de refrigeradores evita a liberação desses gases.
        
        **Importante:** No nosso programa, **não aceitamos a Linha Branca** para descarte, pois esses 
        equipamentos requerem logística especial e empresas especializadas para o manejo seguro dos gases.
        
        ---
        
        #### 🟫 Linha Marrom
        **Equipamentos de áudio, vídeo e informática**
        
        **Exemplos:** Televisores, computadores, notebooks, monitores, DVDs, aparelhos de som
        
        **Por que são perigosos?**
        - Contêm **chumbo** nas telas antigas (TVs de tubo e monitores CRT)
        - Presença de **mercúrio** nas lâmpadas de LCD
        - **Retardantes de chama bromados** nos plásticos
        
        Segundo estudo publicado na revista *Environmental Science & Technology* (2013), monitores 
        e TVs antigas podem conter até 3kg de chumbo por unidade.
        
        ---
        
        #### 🟦 Linha Azul
        **Eletrodomésticos portáteis e pequenos**
        
        **Exemplos:** Liquidificadores, batedeiras, ferros de passar, secadores, ventiladores, aspiradores
        
        **Por que são perigosos?**
        - Componentes plásticos com **aditivos tóxicos**
        - Motores com **cobre** e outros metais
        - Cabos elétricos com revestimento de **PVC**
        
        ---
        
        #### 🟩 Linha Verde
        **Eletrônicos portáteis e acessórios**
        
        **Exemplos:** Celulares, tablets, baterias, carregadores, fones de ouvido, smartwatches
        
        **Por que são perigosos?**
        - Baterias de lítio podem **explodir ou pegar fogo** se perfuradas
        - Contêm **cobalto, níquel e cádmio**
        - Placas eletrônicas com **ouro, prata e paládio** (mas também metais tóxicos)
        
        Pesquisadores da Universidade Federal de Minas Gerais (UFMG) identificaram que um único 
        celular pode conter mais de 40 elementos da tabela periódica, incluindo metais preciosos 
        e substâncias tóxicas.
        
        **Fonte:** RODRIGUES, A. C. Impactos socioambientais dos resíduos de equipamentos elétricos 
        e eletrônicos: estudo da cadeia pós-consumo no Brasil. Tese (Doutorado) - Faculdade de 
        Engenharia, Arquitetura e Urbanismo, Universidade Metodista de Piracicaba, 2007.
        """)

    with tab3:
        st.markdown("""
        ### 🌍 Impactos do Lixo Eletrônico
        
        #### 💧 Contaminação Ambiental
        
        Quando descartado incorretamente em lixões ou aterros comuns, o lixo eletrônico libera 
        **metais pesados** que contaminam o solo e podem atingir lençóis freáticos.
        
        **Principais contaminantes:**
        - **Chumbo (Pb):** afeta o sistema nervoso, rins e reprodução
        - **Mercúrio (Hg):** causa danos neurológicos graves
        - **Cádmio (Cd):** cancerígeno e prejudica ossos e rins
        - **Cromo hexavalente (Cr VI):** altamente tóxico e cancerígeno
        
        Um estudo conduzido por pesquisadores da Universidade de São Paulo (USP) e publicado 
        na revista *Science of The Total Environment* (2016) detectou concentrações elevadas 
        de metais pesados no solo de áreas próximas a locais de descarte irregular de 
        eletrônicos na região metropolitana de São Paulo.
        
        ---
        
        #### ⚕️ Riscos à Saúde Humana
        
        A Organização Mundial da Saúde (OMS) alerta que a exposição a componentes tóxicos do 
        lixo eletrônico pode causar:
        
        - Doenças respiratórias
        - Problemas neurológicos (especialmente em crianças)
        - Câncer
        - Danos aos rins e fígado
        - Alterações hormonais
        
        Dr. Karin Bodewits, especialista em saúde ambiental da OMS, destacou em 2021 que 
        "crianças e mulheres grávidas são particularmente vulneráveis aos efeitos tóxicos 
        do lixo eletrônico, pois essas substâncias podem atravessar a placenta e afetar 
        o desenvolvimento fetal".
        
        ---
        
        #### 📊 Cenário Brasileiro
        
        Segundo relatório da Associação Brasileira de Empresas de Limpeza Pública e Resíduos 
        Especiais (Abrelpe, 2022):
        
        - Brasil gerou aproximadamente **2,4 milhões de toneladas** de lixo eletrônico em 2021
        - Isso representa cerca de **11,3 kg por habitante**
        - Menos de **3%** é reciclado formalmente
        - Brasil é o maior gerador de e-lixo da América Latina
        
        ---
        
        #### ✅ A Importância da Reciclagem
        
        Segundo pesquisa do Dr. Ruediger Kuehr, diretor do programa SCYCLE da Universidade 
        das Nações Unidas (UNU), reciclar uma tonelada de placas de circuito eletrônico pode 
        recuperar:
        
        - 40 a 800 vezes mais ouro que uma tonelada de minério
        - 30 a 40 vezes mais cobre
        
        Além disso, a reciclagem adequada evita que substâncias tóxicas contaminem o meio 
        ambiente e permite a recuperação de materiais valiosos.
        
        ---
        
        ### 📚 Referências Bibliográficas
        
        1. FORTI, V. et al. **The Global E-waste Monitor 2020**. United Nations University (UNU), 2020.
        
        2. RODRIGUES, A. C. **Impactos socioambientais dos resíduos de equipamentos elétricos e 
        eletrônicos: estudo da cadeia pós-consumo no Brasil**. Tese (Doutorado) - UNIMEP, 2007.
        
        3. ABRELPE. **Panorama dos Resíduos Sólidos no Brasil 2022**. Associação Brasileira de 
        Empresas de Limpeza Pública e Resíduos Especiais, 2022.
        
        4. WORLD HEALTH ORGANIZATION. **Children and Digital Dumpsites: E-waste exposure and 
        child health**. WHO, 2021.
        
        5. ROBINSON, B. H. **E-waste: An assessment of global production and environmental impacts**. 
        Science of The Total Environment, v. 408, n. 2, p. 183-191, 2009.
        """)

    if st.button("🏠 Voltar ao Dashboard", use_container_width=True):
        st.session_state.screen = 'dashboard'
        st.rerun()

def jogos_screen():
    st.markdown("<h1>♻️ Eco Eletrônico</h1><h2>🎮 Quiz & Jogos</h2>", unsafe_allow_html=True)

    # Inicializar estados se não existirem
    if 'quiz_completo' not in st.session_state:
        st.session_state.quiz_completo = False
    if 'classificacao_completo' not in st.session_state:
        st.session_state.classificacao_completo = False
    if 'cruzadinha_completo' not in st.session_state:
        st.session_state.cruzadinha_completo = False
    if 'jogos_recompensa_recebida' not in st.session_state:
        st.session_state.jogos_recompensa_recebida = False

    # Verificar progresso
    quiz_icon = "✅" if st.session_state.quiz_completo else "⬜"
    classif_icon = "✅" if st.session_state.classificacao_completo else "⬜"
    cruzadinha_icon = "✅" if st.session_state.cruzadinha_completo else "⬜"

    st.info(f"""💡 **Complete os 3 jogos PERFEITAMENTE e ganhe 1 ponto!**
    
**Progresso:**
{quiz_icon} Quiz (5/5 corretas)
{classif_icon} Classificação (6/6 corretas)
{cruzadinha_icon} Cruzadinha (6/6 corretas)
    """)

    # Verificar se completou todos
    if st.session_state.quiz_completo and st.session_state.classificacao_completo and st.session_state.cruzadinha_completo:
        if not st.session_state.jogos_recompensa_recebida:
            st.balloons()
            st.success("🎉 PARABÉNS! Você completou TODOS os jogos perfeitamente!")
            st.success("⭐ Ganhou 1 ponto!")
            update_points(st.session_state.user['id'], 1)
            sync_user()
            st.session_state.jogos_recompensa_recebida = True
        else:
            st.success("✅ Você já completou todos os jogos e recebeu sua recompensa!")
            if st.button("🔄 Resetar Progresso e Jogar Novamente", use_container_width=True):
                st.session_state.quiz_completo = False
                st.session_state.classificacao_completo = False
                st.session_state.cruzadinha_completo = False
                st.session_state.jogos_recompensa_recebida = False
                st.rerun()

    tab1, tab2, tab3 = st.tabs(["📝 Quiz", "🎯 Jogo da Classificação", "🔤 Cruzadinha"])

    with tab1:
        quiz_game()

    with tab2:
        classificacao_game()

    with tab3:
        cruzadinha_game()

    if st.button("🏠 Voltar ao Dashboard", use_container_width=True):
        st.session_state.screen = 'dashboard'
        st.rerun()

def quiz_game():
    st.markdown("### 📝 Quiz do Lixo Eletrônico")

    if st.session_state.quiz_completo:
        st.success("✅ Quiz completo! Continue com os outros jogos.")
        return

    st.markdown("**Responda as 5 perguntas corretamente!**")

    # Pool de perguntas (será embaralhado)
    todas_perguntas = [
        {
            'pergunta': '📱 Quantas toneladas de lixo eletrônico foram geradas no mundo em 2019?',
            'opcoes': ['25,6 milhões', '53,6 milhões', '100 milhões', '10 milhões'],
            'resposta': '53,6 milhões',
        },
        {
            'pergunta': '🟫 Qual metal pesado é encontrado em TVs de tubo antigas?',
            'opcoes': ['Ouro', 'Prata', 'Chumbo', 'Alumínio'],
            'resposta': 'Chumbo',
        },
        {
            'pergunta': '♻️ Qual porcentagem do lixo eletrônico é reciclada adequadamente?',
            'opcoes': ['50%', '30%', '17,4%', '5%'],
            'resposta': '17,4%',
        },
        {
            'pergunta': '🟩 Qual perigo as baterias de lítio representam se perfuradas?',
            'opcoes': ['Podem derreter', 'Podem explodir', 'Liberam oxigênio', 'Nenhum perigo'],
            'resposta': 'Podem explodir',
        },
        {
            'pergunta': '🇧🇷 Quantos kg de e-lixo cada brasileiro gera por ano?',
            'opcoes': ['5 kg', '11,3 kg', '20 kg', '2 kg'],
            'resposta': '11,3 kg',
        },
        {
            'pergunta': '🟥 Por que não aceitamos geladeiras no programa?',
            'opcoes': ['São muito pesadas', 'Contêm gases CFC perigosos', 'Custam muito caro', 'Não têm valor'],
            'resposta': 'Contêm gases CFC perigosos',
        },
        {
            'pergunta': '🌍 Qual metal pode ser recuperado 800x mais em placas eletrônicas que no minério?',
            'opcoes': ['Ferro', 'Cobre', 'Ouro', 'Alumínio'],
            'resposta': 'Ouro',
        },
    ]

    # Embaralhar perguntas e selecionar 5
    if 'quiz_perguntas_selecionadas' not in st.session_state:
        perguntas_embaralhadas = random.sample(todas_perguntas, 5)
        # Embaralhar também as opções de cada pergunta
        for p in perguntas_embaralhadas:
            opcoes_embaralhadas = p['opcoes'].copy()
            random.shuffle(opcoes_embaralhadas)
            p['opcoes_embaralhadas'] = opcoes_embaralhadas
        st.session_state.quiz_perguntas_selecionadas = perguntas_embaralhadas

    perguntas = st.session_state.quiz_perguntas_selecionadas

    if 'quiz_respostas' not in st.session_state:
        st.session_state.quiz_respostas = {}

    for i, q in enumerate(perguntas):
        st.markdown(f"**{i+1}. {q['pergunta']}**")
        resposta = st.radio(f"Escolha sua resposta:", q['opcoes_embaralhadas'], key=f"quiz_{i}", label_visibility="collapsed")
        st.session_state.quiz_respostas[i] = resposta
        st.markdown("---")

    if st.button("✅ Enviar Respostas", use_container_width=True):
        acertos = 0

        for i, q in enumerate(perguntas):
            if st.session_state.quiz_respostas.get(i) == q['resposta']:
                acertos += 1

        if acertos == 5:
            st.success("✅ Quiz completo! Você acertou todas as perguntas!")
            st.session_state.quiz_completo = True
            st.session_state.quiz_perguntas_selecionadas = None  # Resetar para próxima vez
            st.rerun()
        else:
            st.warning(f"❌ Você acertou {acertos}/5. Precisa acertar TODAS para completar!")

def classificacao_game():
    st.markdown("### 🎯 Jogo da Classificação")

    if st.session_state.classificacao_completo:
        st.success("✅ Classificação completa! Continue com os outros jogos.")
        return

    st.markdown("**Classifique TODOS os itens corretamente!**")

    # Pool de itens (será embaralhado)
    todos_itens = [
        {'nome': '📱 Celular', 'linha_correta': 'Linha Verde'},
        {'nome': '💻 Notebook', 'linha_correta': 'Linha Marrom'},
        {'nome': '🌀 Ventilador', 'linha_correta': 'Linha Azul'},
        {'nome': '🔋 Bateria', 'linha_correta': 'Linha Verde'},
        {'nome': '📺 Televisor', 'linha_correta': 'Linha Marrom'},
        {'nome': '☕ Liquidificador', 'linha_correta': 'Linha Azul'},
        {'nome': '🎧 Fone de Ouvido', 'linha_correta': 'Linha Verde'},
        {'nome': '🖥️ Monitor', 'linha_correta': 'Linha Marrom'},
    ]

    # Embaralhar e selecionar 6 itens
    if 'classif_itens_selecionados' not in st.session_state:
        st.session_state.classif_itens_selecionados = random.sample(todos_itens, 6)

    itens = st.session_state.classif_itens_selecionados
    linhas = ['Linha Marrom', 'Linha Azul', 'Linha Verde']

    if 'classif_respostas' not in st.session_state:
        st.session_state.classif_respostas = {}

    for i, item in enumerate(itens):
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"**{item['nome']}**")
        with col2:
            resposta = st.selectbox("Pertence à:", linhas, key=f"classif_{i}", label_visibility="collapsed")
            st.session_state.classif_respostas[i] = resposta

    if st.button("✅ Verificar Classificação", use_container_width=True):
        acertos = 0

        for i, item in enumerate(itens):
            if st.session_state.classif_respostas.get(i) == item['linha_correta']:
                acertos += 1

        if acertos == len(itens):
            st.success("✅ Classificação completa! Todos os itens corretos!")
            st.session_state.classificacao_completo = True
            st.session_state.classif_itens_selecionados = None  # Resetar
            st.rerun()
        else:
            st.warning(f"❌ Você acertou {acertos}/{len(itens)}. Precisa acertar TODOS!")

def cruzadinha_game():
    st.markdown("### 🔤 Cruzadinha Ecológica")

    if st.session_state.cruzadinha_completo:
        st.success("✅ Cruzadinha completa! Continue com os outros jogos.")
        return

    st.markdown("**Preencha todas as palavras corretamente!**")

    # Palavras da cruzadinha (embaralhadas)
    todas_palavras = [
        {'dica': '📱 Equipamento portátil para fazer ligações', 'resposta': 'CELULAR'},
        {'dica': '🟫 Metal pesado encontrado em TVs antigas', 'resposta': 'CHUMBO'},
        {'dica': '♻️ Processo de transformar lixo em novos produtos', 'resposta': 'RECICLAGEM'},
        {'dica': '🔋 Componente que armazena energia elétrica', 'resposta': 'BATERIA'},
        {'dica': '🟩 Tipo de bateria que pode explodir se perfurada', 'resposta': 'LITIO'},
        {'dica': '💻 Equipamento eletrônico para trabalho e estudos', 'resposta': 'COMPUTADOR'},
        {'dica': '🌍 Continente que mais gera lixo eletrônico', 'resposta': 'ASIA'},
        {'dica': '⚠️ Metal tóxico que afeta o sistema nervoso', 'resposta': 'MERCURIO'},
    ]

    # Embaralhar e selecionar 6 palavras
    if 'cruzadinha_palavras_selecionadas' not in st.session_state:
        st.session_state.cruzadinha_palavras_selecionadas = random.sample(todas_palavras, 6)

    palavras = st.session_state.cruzadinha_palavras_selecionadas

    if 'cruzadinha_respostas' not in st.session_state:
        st.session_state.cruzadinha_respostas = {}

    for i, palavra in enumerate(palavras):
        st.markdown(f"**{i+1}. {palavra['dica']}**")
        resposta = st.text_input(f"Resposta {i+1}:", key=f"cruz_{i}", max_chars=15).upper().strip()
        st.session_state.cruzadinha_respostas[i] = resposta
        st.markdown("---")

    if st.button("✅ Verificar Cruzadinha", use_container_width=True):
        acertos = 0

        for i, palavra in enumerate(palavras):
            if st.session_state.cruzadinha_respostas.get(i) == palavra['resposta']:
                acertos += 1

        if acertos == len(palavras):
            st.success("✅ Cruzadinha completa! Todas as palavras corretas!")
            st.session_state.cruzadinha_completo = True
            st.session_state.cruzadinha_palavras_selecionadas = None  # Resetar
            st.rerun()
        else:
            st.warning(f"❌ Você acertou {acertos}/{len(palavras)}. Precisa acertar TODAS!")
    st.markdown("### 🃏 Jogo da Memória Ecológica")

    if st.session_state.memoria_completo:
        st.success("✅ Jogo da Memória completo! Continue com os outros jogos.")
        return

    st.markdown("**Encontre todos os pares!**")

    pares = [
        ('📱', 'Celular'),
        ('💻', 'Notebook'),
        ('🔋', 'Bateria'),
        ('📺', 'TV'),
        ('🌀', 'Ventilador'),
        ('☕', 'Liquidificador'),
    ]

    if 'memoria_cartas' not in st.session_state or len(st.session_state.memoria_cartas) == 0:
        cartas = []
        for emoji, nome in pares:
            cartas.append({'id': f'{emoji}_1', 'conteudo': emoji, 'par': nome, 'virada': False})
            cartas.append({'id': f'{nome}_2', 'conteudo': nome, 'par': emoji, 'virada': False})
        random.shuffle(cartas)
        st.session_state.memoria_cartas = cartas
        st.session_state.memoria_selecionadas = []
        st.session_state.memoria_acertos = 0

    st.markdown(f"**Pares encontrados: {st.session_state.memoria_acertos}/{len(pares)}**")

    cols = st.columns(4)
    for i, carta in enumerate(st.session_state.memoria_cartas):
        with cols[i % 4]:
            if carta['virada']:
                st.markdown(f"<div style='text-align: center; padding: 20px; background: #d4edda; border-radius: 10px; margin: 5px;'><h2>{carta['conteudo']}</h2></div>", unsafe_allow_html=True)
            else:
                if st.button("❓", key=f"carta_{i}", use_container_width=True):
                    if len(st.session_state.memoria_selecionadas) < 2:
                        st.session_state.memoria_selecionadas.append(i)
                        st.rerun()

    if len(st.session_state.memoria_selecionadas) == 2:
        idx1, idx2 = st.session_state.memoria_selecionadas
        carta1 = st.session_state.memoria_cartas[idx1]
        carta2 = st.session_state.memoria_cartas[idx2]

        if (carta1['conteudo'] == carta2['par']) or (carta2['conteudo'] == carta1['par']):
            st.session_state.memoria_cartas[idx1]['virada'] = True
            st.session_state.memoria_cartas[idx2]['virada'] = True
            st.session_state.memoria_acertos += 1
            st.success("✅ Par encontrado!")

            if st.session_state.memoria_acertos == len(pares):
                st.success("✅ Jogo da Memória completo!")
                st.session_state.memoria_completo = True
                st.rerun()
        else:
            st.error("❌ Não é um par. Tente novamente!")

        st.session_state.memoria_selecionadas = []

    if st.button("🔄 Reiniciar Jogo", use_container_width=True):
        st.session_state.memoria_cartas = []
        st.session_state.memoria_selecionadas = []
        st.session_state.memoria_acertos = 0
        st.rerun()

def admin_login_screen():
    st.markdown("<h1>♻️ Eco Eletrônico</h1><h2>🔒 Acesso Admin</h2>", unsafe_allow_html=True)
    senha = st.text_input("Senha", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Entrar", use_container_width=True):
            if senha == ADMIN_PASSWORD:
                st.session_state.screen = 'admin'
                st.rerun()
            else:
                st.error("❌ Senha incorreta!")
    with col2:
        if st.button("Voltar", use_container_width=True):
            st.session_state.screen = 'home'
            st.rerun()

def admin_screen():
    st.markdown("<h1>♻️ Eco Eletrônico</h1><h2>⚙️ Painel Admin</h2>", unsafe_allow_html=True)

    if st.button("🚪 Sair"):
        st.session_state.screen = 'home'
        st.rerun()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='stat-card'><p>Usuários</p><h1>{len(st.session_state.usuarios)}</h1></div>", unsafe_allow_html=True)
    with col2:
        total_descartes = len(st.session_state.descartes)
        st.markdown(f"<div class='stat-card'><p>Total Descartes</p><h1>{total_descartes}</h1></div>", unsafe_allow_html=True)
    with col3:
        aprovados = len([d for d in st.session_state.descartes if d['status'] == 'Aprovado'])
        st.markdown(f"<div class='stat-card'><p>Aprovados</p><h1>{aprovados}</h1></div>", unsafe_allow_html=True)
    with col4:
        pend = len([r for r in st.session_state.resgates if r['status'] == 'Pendente'])
        st.markdown(f"<div class='stat-card'><p>Cupons Pendentes</p><h1>{pend}</h1></div>", unsafe_allow_html=True)

    st.markdown("### 📊 Estatísticas por Linha de Lixo")
    linhas_stats = {}
    for d in st.session_state.descartes:
        linha = d.get('linha', 'Desconhecida')
        if linha not in linhas_stats:
            linhas_stats[linha] = {'total': 0, 'quantidade': 0}
        linhas_stats[linha]['total'] += 1
        linhas_stats[linha]['quantidade'] += d.get('quantidade', 0)

    cols = st.columns(3)
    for idx, (linha, stats) in enumerate(linhas_stats.items()):
        with cols[idx % 3]:
            st.markdown(f"""<div class='card-wait'>
                <b>{linha}</b><br>
                Descartes: {stats['total']}<br>
                Itens: {stats['quantidade']}
            </div>""", unsafe_allow_html=True)

    st.markdown("### 🏆 Top 5 Usuários")
    top_users = sorted(st.session_state.usuarios, key=lambda x: x.get('pontos', 0), reverse=True)[:5]
    for i, user in enumerate(top_users, 1):
        descartes_user = len([d for d in st.session_state.descartes if d['usuarioId'] == user['id'] and d['status'] == 'Aprovado'])
        st.markdown(f"""<div class='card-ok'>
            <b>{i}º - {user['nome']}</b> ({user['turma']})<br>
            Pontos: {user['pontos']:.1f} | Descartes aprovados: {descartes_user}
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### ⏳ Descartes Pendentes")
    descartes_pend = [d for d in st.session_state.descartes if d['status'] == 'Pendente']

    if descartes_pend:
        for d in descartes_pend:
            user = next((u for u in st.session_state.usuarios if u['id'] == d['usuarioId']), None)

            eh_customizado = d.get('customizado', False)
            badge_custom = " 🔖 <span style='color: #ff6b6b;'>CUSTOMIZADO</span>" if eh_customizado else ""

            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.markdown(f"""<div class='card-wait'>
                    <b>Nº:</b> {d['numero']} | <b>Aluno:</b> {user['nome'] if user else 'N/A'} ({user['turma'] if user else 'N/A'}){badge_custom}<br>
                    <b>Linha:</b> {d['linha']} | <b>Material:</b> {d['material']} ({d['quantidade']} un) | <b>Pontos:</b> {d['pontos']}<br>
                    <small>{d['data']}</small></div>""", unsafe_allow_html=True)
            with col2:
                if st.button("✅", key=f"aprovar_{d['id']}", use_container_width=True):
                    d['status'] = 'Aprovado'
                    update_points(d['usuarioId'], d['pontos'])
                    st.rerun()
            with col3:
                if st.button("❌", key=f"recusar_desc_{d['id']}", use_container_width=True):
                    d['status'] = 'Recusado'
                    save_db()
                    st.rerun()
    else:
        st.info("Nenhum descarte pendente")

    st.markdown("### 🎫 Cupons Pendentes")
    cupons_pend = [r for r in st.session_state.resgates if r['status'] == 'Pendente']

    if cupons_pend:
        for r in cupons_pend:
            user = next((u for u in st.session_state.usuarios if u['id'] == r['usuarioId']), None)
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"""<div class='card-wait'>
                    <b>Código:</b> {r['codigo']} | <b>Aluno:</b> {user['nome'] if user else 'N/A'} ({user['turma'] if user else 'N/A'})<br>
                    <b>Cupom:</b> {r['categoria']} - {r['cupom']} ({r['pontos']} pts)<br>
                    <small>{r['data']}</small></div>""", unsafe_allow_html=True)
            with col2:
                if st.button("✅", key=f"aprovar_cupom_{r['id']}", use_container_width=True):
                    r['status'] = 'Aprovado'
                    save_db()
                    st.rerun()
            with col3:
                if st.button("❌", key=f"recusar_{r['id']}", use_container_width=True):
                    r['status'] = 'Recusado'
                    update_points(r['usuarioId'], r['pontos'])
                    st.rerun()
    else:
        st.info("Nenhum cupom pendente")

def main():
    load_db()
    screen = st.session_state.get('screen', 'home')

    if screen == 'home':
        home_screen()
    elif screen == 'cadastro':
        cadastro_screen()
    elif screen == 'login':
        login_screen()
    elif screen == 'dashboard':
        if st.session_state.user:
            dashboard_screen()
        else:
            st.session_state.screen = 'home'
            st.rerun()
    elif screen == 'cadastrar_eletro':
        cadastrar_eletro_screen()
    elif screen == 'cupons':
        cupons_screen()
    elif screen == 'resgates':
        resgates_screen()
    elif screen == 'aprendizagem':
        aprendizagem_screen()
    elif screen == 'jogos':
        jogos_screen()
    elif screen == 'admin_login':
        admin_login_screen()
    elif screen == 'admin':
        admin_screen()
    else:
        st.session_state.screen = 'home'
        st.rerun()

if __name__ == "__main__":
    main()
