import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Carregar ou criar dados na session_state
if "df" not in st.session_state or "portas_por_caminho" not in st.session_state:
    # Exemplo de carregar dados (substitua pelo seu método real)
    df = pd.read_excel('data/base.xlsx')
    
    # Calcula total portas por caminho de rede
    portas_por_caminho = df.groupby('CAMINHO_REDE')['PORTAS'].sum().to_dict()
    
    # Armazena na session_state
    st.session_state.df = df
    st.session_state.portas_por_caminho = portas_por_caminho

# Função para obter status usando portas_por_caminho da session_state
def obter_status(row):
    total = st.session_state.portas_por_caminho.get(row["CAMINHO_REDE"], 0)
    if total > 128:
        return "🔴 SATURADO"
    elif total == 128 and row["PORTAS"] == 16:
        return "🔴 SATURADO"
    elif total == 128 and row["PORTAS"] == 8:
        return "🔴 CTO É SP8 MAS PON JÁ ESTÁ SATURADA"
    elif row["PORTAS"] == 16 and total < 128:
        return "✅ CTO JÁ É SP16 MAS A PON NÃO ESTÁ SATURADA"
    elif row["PORTAS"] == 8 and total < 128:
        return "✅ TROCA DE SP8 PARA SP16"
    else:
        return "⚪ STATUS INDEFINIDO"

# Aplica o status só uma vez e guarda no session_state para não repetir sempre
if "df_status" not in st.session_state:
    df = st.session_state.df.copy()
    df["STATUS"] = df.apply(obter_status, axis=1)
    st.session_state.df_status = df
else:
    df = st.session_state.df_status

# Define os grupos
status_nao_usar = [
    "🔴 SATURADO",
    "🔴 CTO É SP8 MAS PON JÁ ESTÁ SATURADA"
]
status_pode_usar = [
    "✅ CTO JÁ É SP16 MAS A PON NÃO ESTÁ SATURADA",
    "✅ TROCA DE SP8 PARA SP16"
]

df_nao_usar = df[df["STATUS"].isin(status_nao_usar)]
df_pode_usar = df[df["STATUS"].isin(status_pode_usar)]

# Interface Streamlit
st.title("📍 Mapa de CTOs com Filtros")

grupo = st.selectbox(
    "Selecione o grupo de CTOs para mostrar no mapa:",
    options=["CTOs que NÃO podemos usar", "CTOs que podemos usar"]
)

df_mapa = df_nao_usar if grupo == "CTOs que NÃO podemos usar" else df_pode_usar

if df_mapa.empty:
    st.warning("Nenhum dado encontrado para o grupo selecionado.")
else:
    lat_centro = df_mapa["LAT"].mean()
    lon_centro = df_mapa["LONG"].mean()
    m = folium.Map(location=[lat_centro, lon_centro], zoom_start=14)
    cor = "red" if grupo == "CTOs que NÃO podemos usar" else "green"

    for _, row in df_mapa.iterrows():
        folium.Marker(
            location=[row["LAT"], row["LONG"]],
            tooltip=f"CTO: {row['CTO']}",
            popup=f"Status: {row['STATUS']}\nPortas: {row['PORTAS']}\nCaminho: {row['CAMINHO_REDE']}",
            icon=folium.Icon(color=cor)
        ).add_to(m)

    st_folium(m, width=700, height=500)
