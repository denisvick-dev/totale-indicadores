import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# =========================================
# CONFIGURAÇÃO
# =========================================

st.set_page_config(
    page_title="Quantidade de OS",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Quantidade de OS")

# Validar se o arquivo existe no session_state antes de prosseguir
if "df_producao" not in st.session_state or st.session_state["df_producao"] is None:
    st.warning("⚠️ Nenhum dado encontrado. Por favor, faça o upload dos dados na página inicial.")
    st.stop()

# =========================================
# LEITURA E TRATAMENTO DAS ABAS
# =========================================

arquivo_excel = st.session_state["df_producao"]
try:
    prod = pd.read_excel(arquivo_excel, sheet_name='Prod')
except Exception as e:
    st.error(f"Erro ao ler o arquivo Excel: {e}")
    st.stop()

total_os = len(prod)
df = pd.DataFrame(prod)

# =========================================
# FILTROS (SIDEBAR)
# =========================================

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
# EXIBIÇÃO DOS DADOS
# =========================================

col1, col2 = st.columns(2)

with col1:
   st.subheader("Quantidade de OS por Supervisor")

   qtde_os_supervisor = (
      df.groupby(['Supervisor'])['OS']
      .count().reset_index(name='Qtde. de O.S.')
   )

   st.dataframe(
      qtde_os_supervisor.sort_values(by='Qtde. de O.S.', ascending=False),
      use_container_width=False,
      width=500,
      hide_index=True
   )

with col2:
   st.subheader("Quantidade de OS por Projeto")

   qtde_os_projeto = (
      df.groupby(['Projeto'])['OS']
      .count().reset_index(name='Qtde. de O.S.')
   )
   
   st.dataframe(
      qtde_os_projeto.sort_values(by='Qtde. de O.S.', ascending=False),
      use_container_width=False,
      width=300,
      hide_index=True
   )