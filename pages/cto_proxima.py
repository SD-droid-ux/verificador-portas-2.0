import streamlit as st
import pandas as pd
import pydeck as pdk

st.title("3. CTOs Próximas")

# Verifica se a base foi carregada no main.py
if "df" not in st.session_state:
    st.warning("⚠️ Por favor, carregue a base de dados na página principal antes de usar esta funcionalidade.")
else:
    df = st.session_state["df"]
    st.write("Visualização rápida da base carregada:")
    st.dataframe(df.head())

    # Verifica se há colunas de coordenadas
    if {"LAT", "LONG"}.issubset(df.columns):
        df_mapa = df.dropna(subset=["LAT", "LONG"]).copy()

        # 🔧 Conversão segura para tipo numérico
        df_mapa["LAT"] = pd.to_numeric(df_mapa["LAT"], errors="coerce")
        df_mapa["LONG"] = pd.to_numeric(df_mapa["LONG"], errors="coerce")

        # 🔍 Filtra coordenadas válidas
        df_mapa = df_mapa[df_mapa["LAT"].between(-90, 90) & df_mapa["LONG"].between(-180, 180)]

        st.subheader("🌎 Mapa Interativo")

        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=pdk.ViewState(
                latitude=-14.2350,
                longitude=-51.9253,
                zoom=4,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=df_mapa,
                    get_position='[LONG, LAT]',
                    get_radius=100,
                    get_color='[255, 0, 0, 160]',
                    pickable=True,
                ),
            ],
            tooltip={"text": "CTO: {CTO}\nCidade: {CIDADE}"},
        ))
    else:
        st.error("A base precisa ter as colunas LAT e LONG com coordenadas geográficas.")
