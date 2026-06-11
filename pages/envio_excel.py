import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Painel de Dados",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Painel de Dados")

ID_PLANILHA = "11Dp9WdZYUrT_LBvfo07Mi8muKXZykU7v"

URL_EXPORTACAO = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{ID_PLANILHA}/export?format=xlsx"
)

# Inicializa Session State
if "df_producao" not in st.session_state:
    st.session_state["df_producao"] = None

@st.cache_data(ttl=300)
def carregar_producao():
    return pd.read_excel(
        URL_EXPORTACAO,
        engine="openpyxl"
    )


def atualizar_dados():
    try:
        st.session_state["df_producao"] = carregar_producao()

    except Exception as erro:
        st.error(f"Erro ao carregar dados: {erro}")

# Primeira carga
if st.session_state.dados is None:
    atualizar_dados()

# Botão de atualização
if st.button("🔄 Atualizar Dados"):
    carregar_producao.clear()
    atualizar_dados()

dados = st.session_state.dados

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Registros",
        len(dados) if dados is not None else 0
    )

with col2:
    st.metric(
        "Total Colunas",
        len(dados.columns) if dados is not None else 0
    )

with col3:
    st.metric(
        "Última Atualização",
        st.session_state.ultima_atualizacao.strftime("%H:%M:%S")
        if st.session_state.ultima_atualizacao
        else "-"
    )

st.divider()

if dados is not None and not dados.empty:
    st.dataframe(
        dados,
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("Nenhum dado encontrado.")