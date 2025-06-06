import streamlit as st
import pandas as pd
from streamlit_google_maps import st_google_maps

st.title("3. CTOs Próximas")

# Verifica se a base foi carregada no main.py
if "df" not in st.session_state:
    st.warning("⚠️ Por favor, carregue a base de dados na página principal antes de usar esta funcionalidade.")
else:
    df = st.session_state["df"]
    st.write("Visualização rápida da base carregada:")
    st.dataframe(df.head())

    # Mapa interativo do Brasil centralizado (aprox coords do Brasil)
    center = {"lat": -14.2350, "lng": -51.9253}
    zoom = 4  # zoom inicial para visualizar estados

    # Exibe o mapa
    st_google_maps(api_key=st.secrets["GOOGLE_MAPS_API_KEY"], center=center, zoom=zoom)
