import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.title("🔍 CTOs Próximas Utilizáveis")

# Verifica se os dados estão disponíveis na sessão
if "df" not in st.session_state or "portas_por_caminho" not in st.session_state:
    st.warning("⚠️ Por favor, faça o upload da base de dados na página inicial antes de acessar esta aba.")
    st.stop()

# Carrega os dados da sessão
df = st.session_state.df.copy()
portas_por_caminho = st.session_state.portas_por_caminho

# Função de status
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

# Aplica o status ao DataFrame
df["STATUS"] = df.apply(obter_status, axis=1)

# Filtros na interface
st.subheader("Filtros")
cidades = df["CIDADE"].dropna().unique().tolist()
cidade_selecionada = st.selectbox("Cidade", ["Todas"] + sorted(cidades))

status_opcoes = [
    "✅ CTO JÁ É SP16 MAS A PON NÃO ESTÁ SATURADA",
    "✅ TROCA DE SP8 PARA SP16",
    "🔴 SATURADO",
    "🔴 CTO É SP8 MAS PON JÁ ESTÁ SATURADA"
]
status_selecionado = st.multiselect(
    "Filtrar por status",
    status_opcoes,
    default=status_opcoes  # Exibe todos por padrão
)

# Aplica os filtros
df_filtrado = df.copy()
if cidade_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["CIDADE"] == cidade_selecionada]
if status_selecionado:
    df_filtrado = df_filtrado[df_filtrado["STATUS"].isin(status_selecionado)]

# Converte coordenadas
df_filtrado["LAT"] = pd.to_numeric(df_filtrado["LAT"], errors="coerce")
df_filtrado["LONG"] = pd.to_numeric(df_filtrado["LONG"], errors="coerce")
df_filtrado = df_filtrado.dropna(subset=["LAT", "LONG"])

# Mapa
st.subheader("📍 Mapa Interativo")

if df_filtrado.empty:
    st.info("Nenhuma CTO encontrada com os filtros selecionados.")
else:
    lat_centro = df_filtrado["LAT"].mean()
    lon_centro = df_filtrado["LONG"].mean()
    m = folium.Map(location=[lat_centro, lon_centro], zoom_start=13)

    for _, row in df_filtrado.iterrows():
        cor = "green" if "✅" in row["STATUS"] else "red"
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

    st_data = st_folium(m, width=800, height=500)

# Exibe tabela abaixo
st.subheader("📋 Tabela de Dados Filtrados")
st.dataframe(df_filtrado.reset_index(drop=True), use_container_width=True)
