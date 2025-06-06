import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.title("📍 Mapa de CTOs com Filtros")

# Simula a criação ou carregamento da base e portas_por_caminho
if "df" not in st.session_state or "portas_por_caminho" not in st.session_state:
    # Substitua aqui pela leitura real do seu arquivo
    df = pd.read_excel('data/base.xlsx')

    # Calcula o total de portas por caminho de rede
    portas_por_caminho = df.groupby('CAMINHO_REDE')['PORTAS'].sum().to_dict()

    # Armazena no session_state
    st.session_state.df = df
    st.session_state.portas_por_caminho = portas_por_caminho

df = st.session_state.df
portas_por_caminho = st.session_state.portas_por_caminho

# Função para definir o status
def obter_status(row):
    total = portas_por_caminho.get(row["CAMINHO_REDE"], 0)
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

# Aplica a coluna STATUS apenas uma vez e salva
if "df_status" not in st.session_state:
    df = df.copy()
    df["STATUS"] = df.apply(obter_status, axis=1)
    st.session_state.df_status = df
else:
    df = st.session_state.df_status

# Definindo os grupos
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

# Seleção do grupo no Streamlit
grupo = st.selectbox(
    "Selecione o grupo de CTOs para mostrar no mapa:",
    options=["CTOs que NÃO podemos usar", "CTOs que podemos usar"]
)

df_mapa = df_nao_usar if grupo == "CTOs que NÃO podemos usar" else df_pode_usar

# Converter LAT e LONG para numérico, removendo linhas inválidas
df_mapa['LAT'] = pd.to_numeric(df_mapa['LAT'], errors='coerce')
df_mapa['LONG'] = pd.to_numeric(df_mapa['LONG'], errors='coerce')
df_mapa = df_mapa.dropna(subset=['LAT', 'LONG'])

if df_mapa.empty:
    st.warning("Nenhum dado com coordenadas válido para o grupo selecionado.")
else:
    lat_centro = df_mapa["LAT"].mean()
    lon_centro = df_mapa["LONG"].mean()
    m = folium.Map(location=[lat_centro, lon_centro], zoom_start=14)
    
    cor = "red" if grupo == "CTOs que NÃO podemos usar" else "green"

    for _, row in df_mapa.iterrows():
        folium.Marker(
            location=[row["LAT"], row["LONG"]],
            tooltip=f"CTO: {row['CTO']}",
            popup=(
                f"Status: {row['STATUS']}<br>"
                f"Portas: {row['PORTAS']}<br>"
                f"Caminho: {row['CAMINHO_REDE']}"
            ),
            icon=folium.Icon(color=cor)
        ).add_to(m)

    st_folium(m, width=700, height=500)
