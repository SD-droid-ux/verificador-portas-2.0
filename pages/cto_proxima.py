import streamlit as st
import pandas as pd

st.title("🔍 Análise de CTOs utilizáveis e não utilizáveis")

# Verifica se os dados foram carregados no main.py
if "df" not in st.session_state or "portas_por_caminho" not in st.session_state:
    st.error("❌ Dados não encontrados. Faça o upload da base no menu principal.")
    st.stop()

# Carrega os dados do session_state
df = st.session_state.df.copy()
portas_por_caminho = st.session_state.portas_por_caminho.copy()

# Filtro por cidade
cidades_disponiveis = sorted(df["CIDADE"].dropna().unique())
cidade_selecionada = st.selectbox("Selecione a cidade:", cidades_disponiveis)

df_filtrado = df[df["CIDADE"] == cidade_selecionada]

# Função de categorização
def classificar_cto(row):
    chave = (row["POP"], row["CHASSI"], row["PLACA"], row["OLT"])
    total = portas_por_caminho.get(chave, 0)

    if total >= 128:
        if row["PORTAS"] == 8:
            return "🔴 CTO É SP8 MAS PON JÁ ESTÁ SATURADA"
        elif row["PORTAS"] == 16:
            return "🔴 SATURADO"
    else:
        if row["PORTAS"] == 16:
            return "✅ CTO JÁ É SP16 MAS A PON NÃO ESTÁ SATURADA"
        elif row["PORTAS"] == 8:
            return "✅ TROCA DE SP8 PARA SP16"

    return "⚠️ DADO INSUFICIENTE"

# Aplica a classificação
df_filtrado["CATEGORIA"] = df_filtrado.apply(classificar_cto, axis=1)

# Separa os dois blocos
ctos_usaveis = df_filtrado[df_filtrado["CATEGORIA"].str.startswith("✅")]
ctos_inviaveis = df_filtrado[df_filtrado["CATEGORIA"].str.startswith("🔴")]

# Exibe resultados
st.subheader("✅ CTOs que PODEMOS usar:")
st.dataframe(ctos_usaveis.reset_index(drop=True), use_container_width=True)

st.subheader("🔴 CTOs que NÃO PODEMOS usar:")
st.dataframe(ctos_inviaveis.reset_index(drop=True), use_container_width=True)
