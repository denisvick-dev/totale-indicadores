import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# ===========================================
# Inicializção da página
# ===========================================

st.set_page_config(
    page_title="Gerenciador Totale - Ativos",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Gerenciador de Dados - Google Sheets")

# ===========================================
# Conexão com Google Sheets
# ===========================================

# 1. Inicializa a conexão com o Google Sheets
conexao = st.connection("gsheets", type=GSheetsConnection)
URL_ATIVOS = "https://docs.google.com/spreadsheets/d/1LQKDcLshC6XSXLBVWaEYSpxrro6uydyU9pwDLc38pEg/edit"

# 2. Leitura dos dados com cache e tratamento de erros
try:
    # ttl=0 garante que os dados sejam buscados em tempo real sem travar no cache
    lista_ativos = conexao.read(spreadsheet=URL_ATIVOS, ttl=0)
    st.success("⚡ Conexão estabelecida e dados sincronizados com o Google Sheets!")
except Exception as erro:
    st.error(f"❌ Falha crítica ao conectar com a planilha: {erro}")
    lista_ativos = pd.DataFrame()

# 3. Bloco de exibição e inteligência de dados
if not lista_ativos.empty:
    # Garante que espaços extras nos nomes das colunas não quebrem os filtros
    lista_ativos.columns = lista_ativos.columns.str.strip()

    # --- PAINEL DE MÉTRICAS (KPIs) ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Registros", len(lista_ativos))
    with col2:
        # Conta quantos técnicos estão explicitamente com a Situação "ATIVO"
        ativos = len(lista_ativos[lista_ativos['Situação'].str.upper() == 'ATIVO']) if 'Situação' in lista_ativos.columns else 0
        st.metric("Técnicos Ativos", ativos)
    with col3:
        # Conta quantos técnicos estão em "FÉRIAS"
        ferias = len(lista_ativos[lista_ativos['Situação'].str.upper() == 'FÉRIAS']) if 'Situação' in lista_ativos.columns else 0
        st.metric("Em Férias", ferias)
    with col4:
        # Conta as bases operacionais distintas
        bases = lista_ativos['Base'].nunique() if 'Base' in lista_ativos.columns else 0
        st.metric("Bases Operadas", bases)

    st.divider()

    # --- FILTROS NA BARRA LATERAL (SIDEBAR) ---
    st.sidebar.header("🎯 Filtros Avançados")
    
    # Filtro por Monitor
    if 'Monitor' in lista_ativos.columns:
        opcoes_monitor = ["Todos"] + sorted(lista_ativos['Monitor'].dropna().unique().tolist())
        monitor_selecionado = st.sidebar.selectbox("Filtrar por Monitor:", opcoes_monitor)
        if monitor_selecionado != "Todos":
            lista_ativos = lista_ativos[lista_ativos['Monitor'] == monitor_selecionado]

    # Filtro por Situação (Ativo, Férias, Inoperante)
    if 'Situação' in lista_ativos.columns:
        opcoes_situacao = ["Todas"] + sorted(lista_ativos['Situação'].dropna().unique().tolist())
        situacao_selecionada = st.sidebar.selectbox("Filtrar por Situação:", opcoes_situacao)
        if situacao_selecionada != "Todas":
            lista_ativos = lista_ativos[lista_ativos['Situação'] == situacao_selecionada]

    # --- TABELA FINAL ---
    st.subheader("📋 Dados Atuais Filtrados")
    st.dataframe(
        lista_ativos, 
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("ℹ️ Nenhum dado foi carregado ou a planilha está vazia.")