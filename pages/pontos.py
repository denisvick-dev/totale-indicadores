import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# =========================================
# CONFIGURAÇÃO
# =========================================

st.set_page_config(
    page_title="Ranking Geral de Pontos",
    page_icon="🏆",
    layout="wide"
)

st.title("🏆 Ranking Geral de Pontos")

# =========================================
# LEITURA E TRATAMENTO DAS ABAS
# =========================================

if "dados" not in st.session_state:

    st.warning("Carregue os dados na página principal primeiro.")
    st.stop()

dados = st.session_state["dados"]

try:
    prod = dados["Prod"].copy()
    gpon = dados["Gpon"].copy()
except KeyError as erro:
    st.error(f"Aba não encontrada: {erro}")
    st.stop()

# Tratamento dos pontos individualmente antes de juntar
prod['Pontos'] = pd.to_numeric(prod['Pontos'], errors='coerce').fillna(0)
gpon['Pontos'] = pd.to_numeric(gpon['Pontos'], errors='coerce').fillna(0)

total_prod = prod['Pontos'].sum()
total_gpon = gpon['Pontos'].sum()
total_geral = total_prod + total_gpon

# =========================================
# JUNTAR DADOS
# =========================================

df = pd.concat([prod, gpon], ignore_index=True)

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


# FILTRO EQUIPE
if 'Nome Equipe' in df.columns:
    equipes_selecionadas = st.sidebar.multiselect(
        "Equipe",
        df['Nome Equipe'].unique(),
        default=df['Nome Equipe'].unique()
    )
    df_filtrado = df[df['Nome Equipe'].isin(equipes_selecionadas)]

# =========================================
# KPIs
# =========================================

col1, col2, col3, col4 = st.columns(4)

# Totais a serem exibidos nos KPIs
total_equipes = df['Nome Equipe'].nunique() if 'Nome Equipe' in df.columns else 0
total_registros = len(df)
total_filtrado = df_filtrado["Pontos"].sum()

col1.metric("Total Pontos (Geral)", f"{total_geral:,.0f}")
col2.metric("Total Pontos (Filtrado)", f"{total_filtrado:,.0f}")
col3.metric("Total Equipes (Filtrado)", total_equipes)
col4.metric("Total Registros (Filtrado)", total_registros)

st.divider()

# =========================================
# COLORINDO O DATAFRAME
# =========================================

def colorir_metas(valor):
    if valor >= 300 and valor < 400:
        cor = 'background-color: #E6FFE6'  # Verde claro
    elif valor >= 400:
        cor = 'background-color: #B8B8FF'  # Azul claro
    else:
        cor = ''
    return cor

# =========================================
# RANKING GERAL
# =========================================

# Inicializa a variável para evitar NameError na exportação
ranking = pd.DataFrame()

if 'Nome Equipe' in df.columns:
    # Criando o agrupamento do Ranking baseado nos dados filtrados
    ranking = (
        df.groupby(["CódAuxEquipe", "Nome Equipe", "Supervisor"])["Pontos"]
        .sum()
        .reset_index()
        .sort_values("Pontos", ascending=False)
    )
    
    # Adicionando a coluna posição
    ranking.insert(0, 'Posição', range(1, len(ranking) + 1))

    # Adicionando a coluna Meta (Exemplo: Meta de 300 pontos para todos, pode ser ajustada conforme necessidade)
    ranking.insert(5, 'Meta', ranking['Pontos'] - 300)
    
    st.subheader("🏅 Ranking Geral de Pontos")

    st.dataframe(
        ranking.style.format({"Pontos": "{:,.2f}", "Meta": "{:,.2f}"}).map(colorir_metas, subset=['Pontos']),
        use_container_width=True,
        height=500,
        hide_index=True
    )

    # =========================================
    # TOP 10 GRÁFICO
    # =========================================

    top10 = ranking.head(10)

    fig = px.bar(
        top10,
        x='Nome Equipe',
        y='Pontos',
        text_auto=True,
        title='Top 10 Equipes por Pontos',
        color='Pontos',
        color_continuous_scale='Oryel'
    )

    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="")

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("⚠️ A coluna 'Nome Equipe' não foi encontrada nos dados para gerar o ranking.")

# =========================================
# EXPORTAR EXCEL
# =========================================

def exportar_excel(dataframe):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Ranking')
    return output.getvalue()

# Só exibe o botão de download se o ranking possuir dados
if not ranking.empty:
    excel = exportar_excel(ranking)

    st.download_button(
        label="📥 Baixar Ranking Excel",
        data=excel,
        file_name="ranking_geral.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Comentário