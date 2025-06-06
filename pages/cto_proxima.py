import streamlit as st
import folium
from streamlit_folium import st_folium

# Título
st.title("Mapa Interativo com CTOs")

# Criação do mapa centralizado
m = folium.Map(location=[-23.55052, -46.63331], zoom_start=14)

# Adicionando marcadores (você pode puxar de um DataFrame depois)
folium.Marker([-23.55052, -46.63331], tooltip="CTO 1").add_to(m)
folium.Marker([-23.55100, -46.63200], tooltip="CTO 2", icon=folium.Icon(color="red")).add_to(m)

# Mostra o mapa no app
st_folium(m, width=700, height=500)
