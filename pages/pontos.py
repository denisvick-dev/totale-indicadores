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
    page_title="Ranking Geral de Pontos",
    page_icon="icons/ranking-da-pagina.png",
    layout="wide"
)

st.title("📈 Ranking Geral de Pontos")

# =========================================
# LEITURA E TRATAMENTO DAS ABAS
# =========================================

if "dados" not in st.session_state:
    st.warning("⚠️ Carregue os dados na página principal primeiro.")
    st.stop()

dados = st.session_state["dados"]

try:
    prod = dados["Prod"].copy()
    gpon = dados["Gpon"].copy()
except KeyError as erro:
    st.error(f"❌ Aba não encontrada: {erro}")
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

# CORREÇÃO: Todos os filtros agora atualizam a mesma variável 'df' sequencialmente

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
    equipes_disponiveis = sorted(df['Nome Equipe'].dropna().unique())
    equipes_selecionadas = st.sidebar.multiselect(
        "Equipe",
        options=equipes_disponiveis,
        default=equipes_disponiveis
    )
    df = df[df['Nome Equipe'].isin(equipes_selecionadas)]

# =========================================
# KPIs
# =========================================

col1, col2, col3, col4 = st.columns(4)

# Totais corrigidos utilizando a variável unificada 'df' (já filtrada)
total_equipes = df['Nome Equipe'].nunique() if 'Nome Equipe' in df.columns else 0
total_registros = len(df)
total_filtrado = df["Pontos"].sum() if "Pontos" in df.columns else 0

col1.metric("Total Pontos (Geral)", f"{total_geral:,.0f}")
col2.metric("Total Pontos (Filtrado)", f"{total_filtrado:,.0f}")
col3.metric("Total Equipes (Filtrado)", total_equipes)
col4.metric("Total Registros (Filtrado)", total_registros)

st.divider()

# =========================================
# INFORMAÇÕES DE ATUALIZAÇÃO
# =========================================

ultima_atualizacao = df['Data Agendamento'].max() if 'Data Agendamento' in df.columns else None

hoje = datetime.date.today()
ano_atual = hoje.year
mes_atual = hoje.month

_, ultimo_dia_num = calendar.monthrange(ano_atual, mes_atual)
ult_dia = datetime.date(ano_atual, mes_atual, ultimo_dia_num)

# CORREÇÃO: Convertendo as datas explicitamente para string/ISO padrão do numpy para evitar conflito de tipos
data_inicio_np = np.datetime64(ultima_atualizacao.date() if pd.notna(ultima_atualizacao) else hoje)
data_fim_np = np.datetime64(ult_dia) + np.timedelta64(1, 'D')

dias_faltantes = np.busday_count(
    data_inicio_np,
    data_fim_np,
    weekmask="1111110"  # Segunda a Sábado
)

# =========================================
# COLORINDO O DATAFRAME
# =========================================

def colorir_metas(valor):
    if valor >= 300 and valor < 400:
        return 'background-color: #E6FFE6'  # Verde claro
    elif valor >= 400:
        return 'background-color: #B8B8FF'  # Azul claro
    return ''

# =========================================
# RANKING GERAL
# =========================================

ranking = pd.DataFrame()

if 'Nome Equipe' in df.columns:
    # Agrupamento baseado nos dados filtrados atualizados
    ranking = (
        df.groupby(["CódAuxEquipe", "Nome Equipe", "Supervisor"])["Pontos"]
        .sum()
        .reset_index()
        .sort_values("Pontos", ascending=False)
    )

# ===========================================================
# CRIAÇÃO DE VARIÁVEIS DE DIAS TRABALHADOS E MÉDIA DE PONTOS
# ===========================================================

    # Cálculo dos dias trabalhados por equipe
    if 'Dias Trab Tecnico' in df.columns:
        max_por_tecnico = df.groupby('Nome Equipe')['Dias Trab Tecnico'].max()
        valores_mapeados = ranking['Nome Equipe'].map(max_por_tecnico)
        dias_trabalhados = valores_mapeados.fillna(0).astype(int)
    else:
        dias_trabalhados = 0

    # Média de pontos por dia trabalhado (Evita divisão por zero)
    media_pontos = ranking['Pontos'] / dias_trabalhados.replace(0, np.nan)


# ================================================
# INSERÇÃO DE COLUNAS DE POSIÇÃO, META E PROJEÇÃO
# ================================================

    ranking.insert(0, 'Posição', range(1, len(ranking) + 1))
    ranking.insert(5, 'Meta', ranking['Pontos'] - 300)
    ranking.insert(6, 'Projeção', ranking['Pontos'] + (media_pontos * dias_faltantes))

# =========================================
# EXIBIÇÃO DO RANKING
# =========================================

    st.subheader("🏅 Ranking Geral de Pontos")

    st.dataframe(
        ranking.style.format({
            "Pontos": "{:,.2f}", 
            "Meta": "{:,.2f}", 
            "Média": "{:,.2f}", 
            "Projeção": "{:,.2f}"
        }).map(colorir_metas, subset=['Pontos']),
        use_container_width=True,
        height=500,
        hide_index=True
    )

    # =========================================
    # TOP 10 GRÁFICO
    # =========================================

    if not ranking.empty:
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
        st.write("")

# CORREÇÃO: Indentação do bloco else ajustada para alinhar com o 'if Nome Equipe in df.columns'
else:
    st.warning("⚠️ A coluna 'Nome Equipe' não foi encontrada nos dados para gerar o ranking.")

if pd.notna(ultima_atualizacao):
    st.info(f"***Última Atualização:*** {pd.to_datetime(ultima_atualizacao).strftime('%d/%m/%Y')}")

# =========================================
# EXPORTAR EXCEL
# =========================================

def exportar_excel(dataframe):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Ranking')
    return output.getvalue()

if not ranking.empty:
    excel = exportar_excel(ranking)

    st.download_button(
        label="📥 Baixar Ranking Excel",
        data=excel,
        file_name="ranking_geral.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )