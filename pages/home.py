import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Home",
    page_icon="icons/totale.ico",
    layout="wide"
)

st.title("PAINEL DE PRODUÇÃO TOTALE")
st.write("Bem-vindo(a) ao painel de produção da TOTALE! Aqui você pode acessar diversos indicadores e análises sobre a produção, além de atualizar os dados para manter tudo sempre atualizado.")
st.info("ℹ️ Para atualizar os dados, entre em 'Atualização de Dados' na barra lateral e siga as instruções.")

st.subheader("Informativos e Dicas")
st.image('images/consultivo_copa.jpg')