import streamlit as st
import pandas as pd
from rapidfuzz import process

st.title("🏢 Buscar MDU (Prédio)")

# Caminho da base
caminho_base = "pages/base_de_dados/base_mdu.xlsx"

# Carregar a base
try:
    df_mdu = pd.read_excel(caminho_base)
except FileNotFoundError:
    st.error("❌ A base de dados dos MDUs não foi encontrada.")
    st.stop()

# 🔎 Mostra as colunas carregadas da base
st.write("🧾 Colunas disponíveis na planilha:")
st.write(df_mdu.columns.tolist())

# Campos possíveis para busca
colunas_busca = ["Endereço", "Smap(Projetos)", "ID Smap", "Nome do Condomínio Bloco"]

# Entrada do usuário
input_busca = st.text_input("Digite o endereço, ID Smap ou nome do MDU:")

def buscar_mdu_flexivel(entrada):
    resultados = []

    for col in colunas_busca:
        if col in df_mdu.columns:
            matches = process.extract(entrada, choices=df_mdu[col].astype(str).unique(), limit=5, score_cutoff=70)
            for match, score, _ in matches:
                encontrados = df_mdu[df_mdu[col].astype(str) == match]
                encontrados["Correspondência"] = f"{col} (score: {score})"
                resultados.append(encontrados)

    if resultados:
        return pd.concat(resultados, ignore_index=True)
    else:
        return pd.DataFrame()

if input_busca:
    with st.spinner("🔍 Buscando MDUs..."):
        mdu_resultados = buscar_mdu_flexivel(input_busca)
        if not mdu_resultados.empty:
            st.success(f"✅ {len(mdu_resultados)} resultado(s) encontrado(s).")
            st.dataframe(mdu_resultados)
        else:
            st.warning("⚠️ Nenhum MDU encontrado com os dados fornecidos.")
