import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import datetime
import calendar
import numpy as np

# =========================================
# CONFIGURAÇÃO
# =========================================

st.set_page_config(
    page_title="Quantidade de O.S.",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Quantidade de O.S.")

# =========================================
# LEITURA E TRATAMENTO DAS ABAS
# =========================================

if "dados" not in st.session_state:
    st.warning("⚠️ Carregue os dados na página principal primeiro.")
    st.stop()

dados = st.session_state["dados"]

try:
    prod = dados["Prod"].copy()
except KeyError as erro:
    st.error(f"Aba não encontrada: {erro}")
    st.stop()

total_os = len(prod)
df = pd.DataFrame(prod)

# Garantir que a coluna de data seja do tipo datetime para evitar quebras no código
if 'Data Agendamento' in df.columns:
    df['Data Agendamento'] = pd.to_datetime(df['Data Agendamento'])

# =========================================
# FILTROS (SIDEBAR)
# =========================================

st.html(
    """
    <style>
    .stSidebar h2 {
        color: #012869 !important; 
        font-size: 26px !important;
        font-weight: 700 !important;
    }
    .stSidebar [data-testid="stWidgetLabel"] p {
        color: #000047 !important; 
        font-size: 16px !important;
        font-weight: 600 !important;
    }
    .stSidebar [data-baseweb="tag"] {
        background-color: #F37C04 !important; 
        color: #FFFFFF !important; 
        border-radius: 4px !important;
    }
    .stSidebar [data-baseweb="tag"] svg {
        fill: #FFFFFF !important;
    }
    </style>
    """
)

st.sidebar.header("Filtros")

# FILTRO PROJETO
if 'Projeto' in df.columns:
    projetos_disponiveis = sorted(df['Projeto'].dropna().unique())
    projetos_selecionados = st.sidebar.multiselect(
        "Projeto",
        options=projetos_disponiveis,
        default=projetos_disponiveis
    )
    df = df[df['Projeto'].isin(projetos_selecionados)]

# FILTRO SUPERVISOR
if 'Supervisor' in df.columns:
    supervisores_disponiveis = sorted(df['Supervisor'].dropna().unique())
    supervisores_selecionados = st.sidebar.multiselect(
        "Supervisor",
        options=supervisores_disponiveis,
        default=supervisores_disponiveis
    )
    df = df[df['Supervisor'].isin(supervisores_selecionados)]

# =========================================
# INFORMAÇÕES DE ATUALIZAÇÃO E DATAS
# =========================================

ultima_atualizacao = df['Data Agendamento'].max() if 'Data Agendamento' in df.columns and not df.empty else None

hoje = datetime.date.today()
ano_atual = hoje.year
mes_atual = hoje.month

_, ultimo_dia_num = calendar.monthrange(ano_atual, mes_atual)
ult_dia = datetime.date(ano_atual, mes_atual, ultimo_dia_num)

data_inicio_np = np.datetime64(ultima_atualizacao.date() if pd.notna(ultima_atualizacao) else hoje)
data_fim_np = np.datetime64(ult_dia) + np.timedelta64(1, 'D')

dias_faltantes = np.busday_count(
    data_inicio_np,
    data_fim_np,
    weekmask="1111110"  # Segunda a Sábado
)

# ===================================================
# CRIAÇÃO DE VARIÁVEIS PARA CÁLCULO DE PROJEÇÕES
# ===================================================

# Cálculo da média de OS diária por supervisor para uma projeção individualizada e correta
if 'Data Agendamento' in df.columns and 'Supervisor' in df.columns and not df.empty:
    media_por_supervisor = df.groupby(['Supervisor', 'Data Agendamento'])['OS'].count().groupby('Supervisor').mean()
else:
    media_por_supervisor = pd.Series(dtype=float)

# Cálculo da média de OS diária por projeto para uma projeção individualizada e correta
if 'Data Agendamento' in df.columns and 'Projeto' in df.columns and not df.empty:
    media_projeto = df.groupby(['Projeto', 'Data Agendamento'])['OS'].count().groupby('Projeto').mean()
else:
    media_projeto = pd.Series(dtype=float)

# =========================================
# EXIBIÇÃO DOS DADOS
# =========================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("Quantidade de OS por Supervisor")

    # 1. Agrupa e conta a quantidade atual de OS por Supervisor
    qtde_os_supervisor = (
        df.groupby(['Supervisor'])['OS']
        .count().reset_index(name='Qtde. de O.S.')
    )

    # 2. Calcula a projeção para cada supervisor utilizando a média individualizada
    media_individual = qtde_os_supervisor['Supervisor'].map(media_por_supervisor).fillna(0)

    # Meta = Quantidade de O.S. atual - 3500 (meta ideal para o mês)
    qtde_os_supervisor['Meta'] = qtde_os_supervisor['Qtde. de O.S.'] - 3500
    
    # Projeção = Total Atual + (Média Diária do Supervisor * Dias Faltantes)
    qtde_os_supervisor['Projeção'] = (qtde_os_supervisor['Qtde. de O.S.'] + (media_individual * dias_faltantes)).astype(int)

    # 3. Exibe o dataframe final e ordenado
    st.dataframe(
        qtde_os_supervisor.sort_values(by='Qtde. de O.S.', ascending=False),
        use_container_width=False,
        width=500,
        hide_index=True
    )

with col2:
    st.subheader("Quantidade de OS por Projeto")

     # 1. Agrupa e conta a quantidade atual de OS por Projeto
    qtde_os_projeto = (
        df.groupby(['Projeto'])['OS']
        .count().reset_index(name='Qtde. de O.S.')
    )

    # 2. Calcula a projeção para cada projeto utilizando a média individualizada
    media_individual = qtde_os_projeto['Projeto'].map(media_projeto).fillna(0)

    # Meta = Quantidade de O.S. atual - 11000 (meta ideal para o mês)
    qtde_os_projeto['Meta'] = qtde_os_projeto['Qtde. de O.S.'] - 11000

    # Projeção = Total Atual + (Média Diária do Projeto * Dias Faltantes)
    qtde_os_projeto['Projeção'] = (qtde_os_projeto['Qtde. de O.S.'] + (media_individual * dias_faltantes)).astype(int)

    # 3. Exibe o dataframe final e ordenado
    st.dataframe(
        qtde_os_projeto.sort_values(by='Qtde. de O.S.', ascending=False),
        use_container_width=False,
        width=500,
        hide_index=True
    )