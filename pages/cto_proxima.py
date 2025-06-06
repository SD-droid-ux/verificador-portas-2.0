import streamlit as st
import pandas as pd

st.set_page_config(page_title="🔍 CTOs Próximas", layout="wide")
st.title("🔍 Análise de CTOs Utilizáveis e Saturadas")

# Verifica se o DataFrame já foi carregado no main.py
if "dataframe" not in st.session_state:
    st.error("⚠️ Nenhum arquivo carregado. Volte à tela inicial e envie a planilha.")
    st.stop()

# Obtém o DataFrame
df = st.session_state.dataframe.copy()

# Filtro por cidade
cidade = st.selectbox("Selecione a cidade:", sorted(df["CIDADE"].dropna().unique()))
df = df[df["CIDADE"] == cidade].copy()

# Normaliza colunas
for col in ["POP", "CHASSI", "PLACA", "OLT"]:
    df[col] = df[col].astype(str).str.strip().str.upper()

df["PORTAS"] = pd.to_numeric(df["PORTAS"], errors="coerce")

# Soma total de portas por grupo
total_portas_por_grupo = df.groupby(["POP", "CHASSI", "PLACA", "OLT"])["PORTAS"].sum().to_dict()

# Função de categorização
def categorizar(row):
    chave = (row["POP"], row["CHASSI"], row["PLACA"], row["OLT"])
    total = total_portas_por_grupo.get(chave, 0)

    if total >= 128:
        return "🔴 SATURADO"
    elif row["PORTAS"] == 16 and total < 128:
        return "✅ CTO JÁ É SP16 MAS A PON NÃO ESTÁ SATURADA"
    elif row["PORTAS"] == 8 and total < 128:
        return "✅ TROCA DE SP8 PARA SP16"
    else:
        return "🔴 SATURADO"

# Aplica categorização
df["CATEGORIA"] = df.apply(categorizar, axis=1)

# Divide os blocos
df_uso = df[df["CATEGORIA"].str.startswith("✅")].copy()
df_n_uso = df[df["CATEGORIA"].str.startswith("🔴")].copy()

# Exibe resultados
st.subheader("✅ CTOs que PODEMOS usar")
st.dataframe(df_uso, use_container_width=True)

st.subheader("🔴 CTOs que NÃO PODEMOS usar")
if df_n_uso.empty:
    st.info("Nenhuma CTO saturada encontrada.")
else:
    st.dataframe(df_n_uso, use_container_width=True)
