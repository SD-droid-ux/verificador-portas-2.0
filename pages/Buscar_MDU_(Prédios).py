import streamlit as st
import pandas as pd
import os
from rapidfuzz import process
import unicodedata
import re

st.title("🏢 Buscar MDU (Prédios)")

# Caminho para a base de dados de MDUs
caminho_mdu = os.path.join("pages", "base_de_dados", "base_mdu.xlsx")

# Carregamento da base com cache
@st.cache_data
def carregar_base_mdu(caminho):
    try:
        df = pd.read_excel(caminho)
        df.columns = df.columns.str.strip()  # Remove espaços em branco
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a base de dados: {e}")
        return pd.DataFrame()

# Função de limpeza de texto
def limpar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    texto = re.sub(r"[^\w\s]", "", texto)
    return texto.strip()

# Carrega a base
df_mdu = carregar_base_mdu(caminho_mdu)

if df_mdu.empty:
    st.stop()

# Define as colunas que serão usadas para busca
colunas_busca = ["Endereço", "Smap(Projetos)", "ID Smap", "Nome do Condomínio Bloco"]

# Cria colunas auxiliares limpas para busca
for col in colunas_busca:
    if col in df_mdu.columns:
        df_mdu[f"{col}_limpo"] = df_mdu[col].astype(str).apply(limpar_texto)

# Campo de busca
input_busca = st.text_input("🔍 Digite o nome, endereço, ID Smap ou Smap do MDU:")

# Função de busca flexível
def buscar_mdu_flexivel(entrada):
    entrada_limpa = limpar_texto(entrada)
    resultados = []

    for col in colunas_busca:
        col_limpo = f"{col}_limpo"
        if col_limpo in df_mdu.columns:
            lista_opcoes = df_mdu[col_limpo].unique()
            matches = process.extract(entrada_limpa, lista_opcoes, limit=15, score_cutoff=60)
            for match, score, _ in matches:
                encontrados = df_mdu[df_mdu[col_limpo] == match].copy()
                encontrados["Correspondência"] = col
                encontrados["Score"] = score
                resultados.append(encontrados)

    if resultados:
        df_resultado = pd.concat(resultados, ignore_index=True)
        df_resultado = df_resultado.sort_values(by="Score", ascending=False)
        return df_resultado
    else:
        return pd.DataFrame()

# Botão de buscar
if st.button("🔎 Buscar MDU"):
    if not input_busca.strip():
        st.warning("⚠️ Digite algo para buscar.")
    else:
        with st.spinner("Buscando MDU..."):
            mdu_resultados = buscar_mdu_flexivel(input_busca)
            if mdu_resultados.empty:
                st.info("Nenhum MDU encontrado com base nos critérios fornecidos.")
            else:
                st.success(f"🔎 {len(mdu_resultados)} resultado(s) encontrado(s):")
                st.dataframe(mdu_resultados)
