import streamlit as st
import pandas as pd

st.set_page_config(page_title="🔍 CTOs Próximas", layout="wide")
st.title("🔍 Análise de CTOs Utilizáveis e Saturadas")

# Verifica se os dados foram carregados no main.py
if "dataframe" not in st.session_state or st.session_state["dataframe"] is None:
    st.error("⚠️ Nenhum arquivo carregado. Volte à tela inicial e envie a planilha.")
    st.stop()

# Carrega os dados salvos pelo main.py
df = st.session_state["dataframe"].copy()

# Verifica se colunas essenciais estão presentes
colunas_necessarias = {"CIDADE", "POP", "CHASSI", "PLACA", "OLT", "PORTAS", "CTO"}
if not colunas_necessarias.issubset(df.columns):
    st.error("❌ A planilha está faltando colunas obrigatórias: " + ", ".join(colunas_necessarias - set(df.columns)))
    st.stop()

# Filtro por cidade
cidade = st.selectbox("Selecione a cidade:", sorted(df["CIDADE"].dropna().unique()))
df = df[df["CIDADE"] == cidade].copy()

# Normaliza colunas
for col in ["POP", "CHASSI", "PLACA", "OLT"]:
    df[col] = df[col].astype(str).str.strip().str.upper()

df["PORTAS"] = pd.to_numeric(df["PORTAS"], errors="coerce").fillna(0).astype(int)

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

# Aplica a categorização
df["CATEGORIA"] = df.apply(categorizar, axis=1)

# Divide em blocos
df_uso = df[df["CATEGORIA"].str.startswith("✅")].copy()
df_n_uso = df[df["CATEGORIA"].str.startswith("🔴")].copy()

# Exibição
st.subheader("✅ CTOs que PODEMOS usar")
st.dataframe(df_uso, use_container_width=True)

st.subheader("🔴 CTOs que NÃO PODEMOS usar")
if df_n_uso.empty:
    st.info("Nenhuma CTO saturada encontrada.")
else:
    st.dataframe(df_n_uso, use_container_width=True)
