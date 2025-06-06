import streamlit as st
import pandas as pd

st.title("3. CTOs Próximas")

# Verifica se a base foi carregada no main.py
if "df" not in st.session_state:
    st.warning("⚠️ Por favor, carregue a base de dados na página principal antes de usar esta funcionalidade.")
else:
    df = st.session_state["df"]
    st.write("Visualização rápida da base carregada:")
    st.dataframe(df.head())
