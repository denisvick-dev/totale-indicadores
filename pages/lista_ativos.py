import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("Gerenciador de Dados - Google Sheets")

# 1. Cria a conexão (puxa automaticamente os dados de secrets.toml)
conexao = st.connection("gsheets", type=GSheetsConnection)

# 2. Lê a planilha tratando possíveis erros de nome de aba
try:
    # CORREÇÃO: Alinhado o nome da aba para "Ativos" conforme a lógica do seu app
    lista_ativos = conexao.read(worksheet="lista_ativos", ttl=0)
    st.success("Conexão estabelecida e aba 'Ativos' carregada!")
except Exception as e:
    # Se a aba "Ativos" não existir, avisa o usuário e tenta carregar a primeira aba
    st.warning(f"Aba 'Ativos' não encontrada. Tentando primeira aba padrão...")
    try:
        lista_ativos = conexao.read(ttl=0)
        st.success("Primeira aba carregada com sucesso!")
    except Exception as erro_geral:
        st.error(f"Falha crítica na conexão: {erro_geral}")
        lista_ativos = pd.DataFrame()  # Evita quebrar o código abaixo

# 3. Exibe os dados na tela se o DataFrame não estiver vazio
st.subheader("Dados Atuais")
if not lista_ativos.empty:
    st.dataframe(lista_ativos, use_container_width=True)
else:
    st.info("Nenhum dado foi carregado.")