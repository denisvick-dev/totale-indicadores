import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Painéis de Produção TOTALE",
    page_icon="🏠",
    layout="wide"
)

def main():
    st.title("Seja bem-vindo aos painéis de Produção TOTALE 🚀")

    home_page = st.Page("pages/app.py", title="Home", icon="🏠", default=True)
    ranking_pontos = st.Page("pages/pontos.py", title="Ranking de Pontos", icon="🏆")
    qtde_os = st.Page("pages/qtde_os.py", title="Quantidade de O.S.", icon="📊")

    # 2. Configurar a navegação passando a lista de páginas
    pg = st.navigation([home_page, ranking_pontos, qtde_os])

    pg.run()

if __name__ == "__main__":
    main()