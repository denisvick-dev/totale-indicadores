import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import datetime
import calendar
import numpy as np
from streamlit_gsheets import GSheetsConnection

# =========================================
# CONFIGURAÇÃO
# =========================================

st.set_page_config(
    page_title="Consultivos",
    page_icon="📋",
    layout="wide",
)

st.title("📋 Total de Consultivos")

st.divider()

# =========================================
# LEITURA E TRATAMENTO DAS ABAS
# =========================================

if "dados_cons" not in st.session_state:
    st.warning("⚠️ Carregue os dados na página principal primeiro.")
    st.stop()

dados = st.session_state["dados_cons"]

try:
    consultivo = dados["Consultivo"].copy()
except KeyError as erro:
    st.error(f"❌ Aba não encontrada: {erro}")
    st.stop()

consultivo["Qtde. Cons."] = pd.to_numeric(
    consultivo["QTDE_CONSULTIVO"], errors="coerce"
).fillna(0).astype(int)

consultivo["Qtde. Prod."] = pd.to_numeric(
    consultivo["QTDE_PRODUTOS"], errors="coerce"
).fillna(0).astype(int)

df = pd.DataFrame(consultivo)

# =========================================
# Conexão com o Google Sheets
# =========================================
conexao = st.connection("gsheets", type=GSheetsConnection)

# Link da planilha de Ativos
URL_ATIVOS = "https://docs.google.com/spreadsheets/d/1LQKDcLshC6XSXLBVWaEYSpxrro6uydyU9pwDLc38pEg/edit"

try:
    with st.spinner("Sincronizando dados com o Google Sheets..."):
        # 1. Puxa Ativos utilizando o driver gsheets nativo
        df_ativos = conexao.read(spreadsheet=URL_ATIVOS, ttl=0)
        df_ativos.columns = df_ativos.columns.str.strip()
except Exception as erro:
    st.error(f"❌ Falha crítica ao conectar com as planilhas: {erro}")
    st.stop()

# =========================================
# MERGE COM OS DADOS DO GOOGLE SHEETS
# =========================================
df["LOGIN NETSALES"] = df["LOGIN NETSALES"].astype(str).str.strip()
df_ativos["Login"] = df_ativos["Login"].astype(str).str.strip()

df_ativos_subset = df_ativos[["Login", "Monitor", "Base"]].drop_duplicates(subset=[
                                                                        "Login"])

df = df.drop(columns=["Monitor", "Base"], errors="ignore")

df = pd.merge(
    df,
    df_ativos_subset,
    left_on="LOGIN NETSALES",
    right_on="Login",
    how="left"
)

df["Monitor"] = df["Monitor"].fillna("Não Identificado").astype(str)
df["Base"] = df["Base"].fillna("Não Identificado").astype(str)

# =========================================
# FILTROS (SIDEBAR)
# =========================================

# Injeção de CSS para personalizar a aparência da Sidebar e dos widgets
st.html("""
    <style>
    /* 1. Altera a cor do texto "Filtros" no topo da Sidebar */
    .stSidebar h2 {
        color: #012869 !important; /* Azul escuro */
        font-size: 26px !important;
        font-weight: 700 !important;
    }

    /* 2. Altera a cor das etiquetas (labels) dos widgets na Sidebar */
    .stSidebar [data-testid="stWidgetLabel"] p {
        color: #000047 !important; /* Azul escuro */
        font-size: 16px !important;
        font-weight: 600 !important;
    }

    /* 3. Altera a cor de fundo e do texto das TAGS SELECIONADAS no multiselect */
    .stSidebar [data-baseweb="tag"] {
        background-color: #F37C04 !important; /* Fundo laranja */
        color: #FFFFFF !important; /* Texto branco */
        border-radius: 4px !important;
    }

    /* 4. Altera a cor do ícone de "X" para fechar a tag */
    .stSidebar [data-baseweb="tag"] svg {
        fill: #FFFFFF !important;
    }
    </style>
    """)

st.sidebar.header("Filtros")

# FILTRO Base
if "Base" in df.columns:
    bases_disponiveis = sorted(df["Base"].dropna().unique())
    bases_selecionados = st.sidebar.multiselect(
        "Base", options=bases_disponiveis, default=bases_disponiveis
    )
    df = df[df["Base"].isin(bases_selecionados)]

# FILTRO Monitor
if "Monitor" in df.columns:
    monitores_disponiveis = sorted(df["Monitor"].dropna().unique())
    monitores_selecionados = st.sidebar.multiselect(
        "Monitor", options=monitores_disponiveis, default=monitores_disponiveis
    )
    df = df[df["Monitor"].isin(monitores_selecionados)]

# =========================================
# COLORINDO O DATAFRAME
# =========================================


def colorir_projecao(valor):
    # Fundo cinza com letra branca
    return "background-color: grey; color: white; font-weight: bold"


def colorir(valor):
    return "background-color: #F2F2F2; font-weight: bold"  # Fundo cinza claro e negrito

# =========================================
# CRIAÇÃO DA TABELA DE CONSULTIVOS
# =========================================


colunas_obrigatorias = ["LOGIN NETSALES", "VENDEDOR",
                        "Monitor", "Base", "Qtde. Cons.", "Qtde. Prod."]

if all(col in df.columns for col in colunas_obrigatorias):

    total_consultivos = (
        df.groupby(["LOGIN NETSALES", "VENDEDOR", "Monitor", "Base"])[
            ["Qtde. Cons.", "Qtde. Prod."]]
        .sum()
        .reset_index()
        .sort_values("Qtde. Cons.", ascending=False)
    )

    # Inserção da coluna de posição (Ranking)
    total_consultivos.insert(
        0, "Posição", range(1, len(total_consultivos) + 1))

    total_consultivos = total_consultivos.rename(columns={
        "Qtde. Cons.": "Total Consultivos",
        "Qtde. Prod.": "Total Produtos"
    })

    total_consultivos["LOGIN NETSALES"] = total_consultivos["LOGIN NETSALES"].astype(
        str)
    total_consultivos["VENDEDOR"] = total_consultivos["VENDEDOR"].astype(str)
    total_consultivos["Monitor"] = total_consultivos["Monitor"].astype(str)

    total_consultivos["Posição"] = total_consultivos["Posição"].astype(int)
    total_consultivos["Total Consultivos"] = total_consultivos["Total Consultivos"].astype(
        int)
    total_consultivos["Total Produtos"] = total_consultivos["Total Produtos"].astype(
        int)

else:
    st.error(
        "⚠️ As colunas necessárias para o ranking não foram encontradas na base de dados.")
    st.write("**Colunas esperadas:**", colunas_obrigatorias)
    st.write("**Colunas encontradas na sua base:**", list(df.columns))
    st.stop()

# =========================================
# KPIs
# =========================================

col1, col2 = st.columns(2)

qtde_cons = (df[["PLANO TV", "PLANO INTERNET"]] != "-").sum().sum()
qtde_prod = df["QTDE_PRODUTOS"] = df["LISTA_PRODUTOS"].apply(len).sum()

col1.metric("Total Consultivos", f"{qtde_cons:,.0f}")
col2.metric("Total Produtos", f"{qtde_prod:,.0f}")

# =========================================
# EXIBIÇÃO DA TABELA DE CONSULTIVOS
# =========================================

st.subheader("👷 Visão por Técnico")

if not total_consultivos.empty:
    st.dataframe(
        total_consultivos.style.format({
            "Total Consultivos": "{:,.0f}",
            "Total Produtos": "{:,.0f}"
        })
        .map(colorir, subset=["Total Consultivos", "Total Produtos"]),
        use_container_width=False,
        height=500,
        hide_index=True,
        # column_config={
        #    "Posição": st.column_config.NumberColumn("Posição"),
        #    "Total Consultivos": st.column_config.NumberColumn("Qtd. Consultivos", alignment="right"),
        #    "Total Produtos": st.column_config.NumberColumn("Qtd. Produtos", alignment="right")
        # }
    )
else:
    st.info("ℹ️ Nenhum registro encontrado para os filtros selecionados.")
