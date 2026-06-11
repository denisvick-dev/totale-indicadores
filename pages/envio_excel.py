import streamlit as st
import pandas as pd

st.title("Painel de Dados - Atualizado via Computador")

# Substitua pelo ID do seu arquivo do Google Drive
ID_ARQUIVO_DRIVE = "113598490206552656776"  # Exemplo: "1a2b3c4d5e6f7g8h9i0j"
URL_EXPORTACAO = f"https://docs.google.com{ID_ARQUIVO_DRIVE}/export?format=xlsx"

# O parâmetro 'ttl' garante que o Streamlit busque o arquivo na nuvem novamente a cada 5 minutos
@st.cache_data(ttl=300) 
def carregar_dados_nuvem():
    try:
        # Lê o arquivo Excel diretamente da URL de exportação pública
        df = pd.read_excel(URL_EXPORTACAO)
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com o Google Drive: {e}")
        return pd.DataFrame()

# Carrega e exibe os dados
dados = carregar_dados_nuvem()

if not dados.empty:
    st.success("Dados carregados com sucesso da nuvem!")
    st.dataframe(dados)
else:
    st.warning("Aguardando conexão ou arquivo vazio.")

# Botão para o usuário forçar a atualização imediata na tela
if st.button("Recarregar Dados Agora"):
    st.cache_data.clear()
    st.rerun()
