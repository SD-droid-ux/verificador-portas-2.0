import streamlit as st
import pandas as pd
from pages import Buscar por CTO, Cto Proxima

st.title("📊 Verificador de Portas")

uploaded_file = st.file_uploader("📂 Envie a planilha Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    df = df.loc[:, ~df.columns.duplicated()]  # remove duplicatas

    # Passa o dataframe para as páginas via session_state ou diretamente
    st.session_state['df'] = df

    aba = st.sidebar.radio("Selecione a aba", ["1. Visão Geral", "2. Buscar por CTO", "3. CTOs Próximas"])

    if aba == "1. Visão Geral":
        # Código da visão geral, usando st.session_state['df']
        buscar_cto.visao_geral(st.session_state['df'])

    elif aba == "2. Buscar por CTO":
        buscar_cto.buscar_cto(st.session_state['df'])

    elif aba == "3. CTOs Próximas":
        ctos_proximas.ctos_proximas(st.session_state['df'])

else:
    st.info("⏳ Por favor, envie a planilha Excel para iniciar a análise.")
