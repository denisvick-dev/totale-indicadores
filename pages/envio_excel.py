import streamlit as st
import pandas as pd
import time
from datetime import datetime, timezone, timedelta

# =========================================
# CONFIGURANDO HORÁRIO DE BRASÍLIA (GMT-3)
# =========================================

fuso = timezone(timedelta(hours=-3))

st.set_page_config(
    page_title="Atualização de Dados",
    page_icon="icons/atualizar-seta.png",
    layout="wide"
)

st.title("🔁 Atualização de Dados")

ID_PLANILHA_PROD = "11Dp9WdZYUrT_LBvfo07Mi8muKXZykU7v"
ID_PLANILHA_CONS = "1K-n9uJOnAQAZAAalhC4IO9M-BVnkN0WM"

URL_EXPORTACAO_PROD = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{ID_PLANILHA_PROD}/export?format=xlsx"
)

URL_EXPORTACAO_CONS = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{ID_PLANILHA_CONS}/export?format=xlsx"
)

# -----------------------------
# Session State
# -----------------------------
if "dados_prod" not in st.session_state:
    st.session_state["dados_prod"] = None

if "dados_cons" not in st.session_state:
    st.session_state["dados_cons"] = None

if "ultima_atualizacao" not in st.session_state:
    st.session_state["ultima_atualizacao"] = None

# -----------------------------
# Carregamento
# -----------------------------


@st.cache_data(ttl=300)
def carregar_dados_prod():
    return pd.read_excel(
        URL_EXPORTACAO_PROD,
        sheet_name=None,
        engine="openpyxl"
    )


@st.cache_data(ttl=300)
def carregar_dados_cons():
    return pd.read_excel(
        URL_EXPORTACAO_CONS,
        sheet_name=None,
        engine="openpyxl"
    )


def atualizar_dados():

    texto = st.empty()
    barra_progresso = st.progress(0)

    try:
        texto.markdown("⏳ Carregando produção...")
        barra_progresso.progress(30)
        dados_prod = carregar_dados_prod()

        texto.markdown("⏳ Carregando consultivos...")
        barra_progresso.progress(60)
        dados_cons = carregar_dados_cons()

        texto.markdown("⚙️ Processando e salvando informações...")
        barra_progresso.progress(90)

        st.session_state["dados_prod"] = dados_prod
        st.session_state["dados_cons"] = dados_cons
        st.session_state["ultima_atualizacao"] = datetime.now(fuso)

        barra_progresso.progress(100)
        time.sleep(1)
        texto.empty()
        barra_progresso.empty()

        return True

    except Exception as erro:
        texto.empty()
        barra_progresso.empty()
        st.error(f"Erro ao carregar dados: {erro}")
        return False


# Primeira carga
if st.session_state["dados_prod"] is None and st.session_state["dados_cons"] is None:
    atualizar_dados()

# Atualização manual
if st.button("Atualizar Dados", icon="🔁"):

    carregar_dados_prod.clear()
    carregar_dados_cons.clear()

    if atualizar_dados():
        st.success("✅ Dados atualizados com sucesso!!")


dados_prod = st.session_state["dados_prod"]
dados_cons = st.session_state["dados_cons"]

prod = dados_prod["Prod"]
cons = dados_cons["Consultivo"]

# -----------------------------
# Indicadores - Bloco 1 (Prod)
# -----------------------------
with st.container(border=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Registros (Produção)", len(prod))

    with col2:
        st.metric("Total Colunas (Produção)", len(prod.columns))

    with col3:
        ultima = st.session_state["ultima_atualizacao"]
        st.metric(
            "Última Atualização",
            ultima.strftime("%d/%m/%Y %H:%M:%S")
            if ultima else "-"
        )

st.dataframe(
    prod,
    use_container_width=True,
    hide_index=True
)

# -----------------------------
# Indicadores - Bloco 2 (Cons)
# -----------------------------
with st.container(border=True):
    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric("Total Registros (Consultivo)", len(cons))

    with col5:
        st.metric("Total Colunas (Consultivo)", len(cons.columns))

    with col6:
        ultima = st.session_state["ultima_atualizacao"]
        st.metric(
            "Última Atualização",
            ultima.strftime("%d/%m/%Y %H:%M:%S")
            if ultima else "-"
        )

st.dataframe(
    cons,
    use_container_width=True,
    hide_index=True

)