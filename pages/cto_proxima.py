import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="🔍 CTO Próxima", layout="wide")
st.title("🔍 Classificação de CTOs Utilizáveis e Saturadas")

# Caminho do arquivo Excel salvo localmente
caminho_arquivo = os.path.join("pages", "base_de_dados", "base.xlsx")

# Carregando os dados da base
@st.cache_data(ttl=600)
def carregar_base():
    try:
        df = pd.read_excel(caminho_arquivo)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a planilha: {e}")
        return None

df = carregar_base()
if df is None:
    st.stop()

# Verificando colunas obrigatórias
colunas_necessarias = {"cid_rede", "pop", "olt", "slot", "pon", "portas", "cto"}
if not colunas_necessarias.issubset(df.columns):
    st.error("❌ A planilha está faltando colunas obrigatórias: " + ", ".join(colunas_necessarias - set(df.columns)))
    st.stop()

# Normalização
for col in ["pop", "olt", "slot", "pon"]:
    df[col] = df[col].astype(str).str.strip().str.upper()

df["portas"] = pd.to_numeric(df["portas"], errors="coerce").fillna(0).astype(int)

# Filtro por cidade
cidade = st.selectbox("Selecione a cidade:", sorted(df["cid_rede"].dropna().unique()))
df = df[df["cid_rede"] == cidade].copy()

# Total de portas por grupo
total_por_grupo = df.groupby(["pop", "olt", "slot", "pon"])["portas"].sum().to_dict()

# Classificação
def classificar(row):
    chave = (row["pop"], row["olt"], row["slot"], row["pon"])
    total = total_por_grupo.get(chave, 0)

    if total >= 128:
        return "🔴 SATURADO"
    elif row["portas"] == 16 and total < 128:
        return "✅ CTO JÁ É SP16 MAS A PON NÃO ESTÁ SATURADA"
    elif row["portas"] == 8 and total < 128:
        return "✅ TROCA DE SP8 PARA SP16"
    else:
        return "🔴 SATURADO"

df["CATEGORIA"] = df.apply(classificar, axis=1)

# Separando categorias
df_pode = df[df["CATEGORIA"].str.startswith("✅")].copy()
df_nao_pode = df[df["CATEGORIA"].str.startswith("🔴")].copy()

# Exibindo resultados
st.subheader("✅ CTOs que PODEM ser trocadas")
st.dataframe(df_pode, use_container_width=True)

st.subheader("🔴 CTOs que NÃO PODEM ser trocadas")
if df_nao_pode.empty:
    st.info("Nenhuma CTO saturada encontrada.")
else:
    st.dataframe(df_nao_pode, use_container_width=True)
