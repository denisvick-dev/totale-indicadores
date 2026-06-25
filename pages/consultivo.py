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
    consultivo["CONSULTIVO"], errors="coerce").fillna(0)
consultivo["Qtde. Prod."] = pd.to_numeric(
    consultivo["PRODUTOS"], errors="coerce").fillna(0)

df = pd.DataFrame(consultivo)

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

# FILTRO EPO
if "EPO" in df.columns:
    epos_disponiveis = sorted(df["EPO"].dropna().unique())
    epos_selecionados = st.sidebar.multiselect(
        "EPO", options=epos_disponiveis, default=epos_disponiveis
    )
    df = df[df["EPO"].isin(epos_selecionados)]

# FILTRO MONITOR
if "MONITOR" in df.columns:
    monitores_disponiveis = sorted(df["MONITOR"].dropna().unique())
    monitores_selecionados = st.sidebar.multiselect(
        "MONITOR", options=monitores_disponiveis, default=monitores_disponiveis
    )
    df = df[df["MONITOR"].isin(monitores_selecionados)]

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
                        "MONITOR", "Qtde. Cons.", "Qtde. Prod."]

if all(col in df.columns for col in colunas_obrigatorias):

    total_consultivos = (
        df.groupby(["LOGIN NETSALES", "VENDEDOR", "MONITOR"])[
            ["Qtde. Cons.", "Qtde. Prod."]]
        .sum()
        .reset_index()
        .sort_values("Qtde. Cons.", ascending=False)
    )

    # Inserção da coluna de posição (Ranking)
    total_consultivos.insert(
        0, "Posição", range(1, len(total_consultivos) + 1))

    # 3. Correção: Renomeação de ambas as colunas calculadas
    total_consultivos = total_consultivos.rename(columns={
        "Qtde. Cons.": "Total Consultivos",
        "Qtde. Prod.": "Total Produtos"
    })

else:
    st.error(
        "⚠️ As colunas necessárias para o ranking não foram encontradas na base de dados.")
    st.stop()

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
