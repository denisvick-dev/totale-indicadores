import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Atualização de Dados",
    page_icon="📂",
    layout="wide"
)

st.title("📂 Atualização de Dados")

ID_PLANILHA = "11Dp9WdZYUrT_LBvfo07Mi8muKXZykU7v"

URL_EXPORTACAO = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{ID_PLANILHA}/export?format=xlsx"
)

# -----------------------------
# Session State
# -----------------------------
if "dados" not in st.session_state:
    st.session_state["dados"] = None

if "ultima_atualizacao" not in st.session_state:
    st.session_state["ultima_atualizacao"] = None


# -----------------------------
# Carregamento
# -----------------------------
@st.cache_data(ttl=300)
def carregar_dados():

    return pd.read_excel(
        URL_EXPORTACAO,
        sheet_name=None,
        engine="openpyxl"
    )


def atualizar_dados():

    try:

        dados = carregar_dados()

        st.session_state["dados"] = dados
        st.session_state["ultima_atualizacao"] = datetime.now()

        return True

    except Exception as erro:

        st.error(f"Erro ao carregar dados: {erro}")
        return False


# Primeira carga
if st.session_state["dados"] is None:
    atualizar_dados()


# Atualização manual
if st.button("🔄 Atualizar Dados"):

    carregar_dados.clear()

    if atualizar_dados():
        st.success("✅ Dados atualizados com sucesso!!")


dados = st.session_state["dados"]

prod = dados["Prod"]

# -----------------------------
# Indicadores
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Registros", len(prod))

with col2:
    st.metric("Total Colunas", len(prod.columns))

with col3:

    ultima = st.session_state["ultima_atualizacao"]

    st.metric(
        "Última Atualização",
        ultima.strftime("%d/%m/%Y %H:%M:%S")
        if ultima else "-"
    )

st.divider()

st.dataframe(
    prod,
    use_container_width=True,
    hide_index=True
)