import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="CTOs Próximas", layout="wide")

st.title("📍 Buscar CTOs Próximas")

# Verifica se os dados estão disponíveis
if "df" not in st.session_state or "portas_por_caminho" not in st.session_state:
    st.warning("⚠️ A base de dados ainda não foi carregada. Volte à página inicial e envie um arquivo Excel.")
    st.stop()

df = st.session_state.df.copy()
portas_por_caminho = st.session_state.portas_por_caminho

# Função para definir o STATUS de cada linha
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

# Aplica a função
df["STATUS"] = df.apply(obter_status, axis=1)

# Filtros interativos
col1, col2, col3 = st.columns(3)

with col1:
    cidades = df["CIDADE"].dropna().unique()
    cidade_selecionada = st.selectbox("🌆 Filtrar por Cidade:", ["Todas"] + sorted(cidades.tolist()))

with col2:
    status_uso = st.selectbox(
        "🟢 CTOs que podemos usar:",
        ["Todos", "✅ TROCA DE SP8 PARA SP16", "✅ CTO JÁ É SP16 MAS A PON NÃO ESTÁ SATURADA"]
    )

with col3:
    status_nao_uso = st.selectbox(
        "🔴 CTOs que NÃO podemos usar:",
        ["Todos", "🔴 SATURADO", "🔴 CTO É SP8 MAS PON JÁ ESTÁ SATURADA"]
    )

# Filtragem de dados
df_filtrado = df.copy()

if cidade_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["CIDADE"] == cidade_selecionada]

if status_uso != "Todos":
    df_filtrado = df_filtrado[df_filtrado["STATUS"] == status_uso]

if status_nao_uso != "Todos":
    df_filtrado = df_filtrado[df_filtrado["STATUS"] == status_nao_uso]

# Exibir colunas disponíveis (ajuda a identificar erros)
st.caption(f"🔎 Colunas disponíveis: {', '.join(df_filtrado.columns)}")

# Valida se há coordenadas para o mapa
if "LAT" not in df_filtrado.columns or "LONG" not in df_filtrado.columns:
    st.error("❌ As colunas LAT e LONG são obrigatórias para exibir o mapa.")
    st.stop()

# Garantir que LAT e LONG sejam números válidos
df_filtrado["LAT"] = pd.to_numeric(df_filtrado["LAT"], errors="coerce")
df_filtrado["LONG"] = pd.to_numeric(df_filtrado["LONG"], errors="coerce")

# Remover linhas com coordenadas inválidas
df_filtrado = df_filtrado.dropna(subset=["LAT", "LONG"])

# Verificação final
if df_filtrado.empty:
    st.error("❌ Nenhuma linha válida com coordenadas encontradas.")
    st.stop()

# Calcular centro do mapa
lat_centro = df_filtrado["LAT"].mean()
lon_centro = df_filtrado["LONG"].mean()

m = folium.Map(location=[lat_centro, lon_centro], zoom_start=13)

# Adiciona marcadores ao mapa
for _, row in df_filtrado.iterrows():
    cor = "green" if "✅" in row["STATUS"] else "red"
    nome_cto = row.get("CTO", "NOME ANTIGO CTO")

    folium.Marker(
        location=[row["LAT"], row["LONG"]],
        tooltip=f"CTO: {nome_cto}",
        popup=(
            f"<b>CTO:</b> {nome_cto}<br>"
            f"<b>Status:</b> {row['STATUS']}<br>"
            f"<b>Portas:</b> {row.get('PORTAS', '-') }<br>"
            f"<b>Caminho:</b> {row.get('CAMINHO_REDE', '-')}"
        ),
        icon=folium.Icon(color=cor)
    ).add_to(m)

# Exibe o mapa
st_data = st_folium(m, width=1200, height=600)

# Tabela com os dados filtrados
st.subheader("📊 Tabela de Dados Filtrados")
st.dataframe(df_filtrado.reset_index(drop=True), use_container_width=True)
