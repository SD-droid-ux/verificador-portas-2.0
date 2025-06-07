import streamlit as st
import pandas as pd
from rapidfuzz import process
import unicodedata
import re

st.title("🏢 Buscar MDU (Prédio)")

# Carregar base
caminho_base = "pages/base_de_dados/base_mdu.xlsx"
try:
    df_mdu = pd.read_excel(caminho_base)
except FileNotFoundError:
    st.error("❌ A base de dados dos MDUs não foi encontrada.")
    st.stop()

# Lista de colunas para busca
colunas_busca = ["Endereço", "Smap(Projetos)", "ID Smap", "Nome do Condomínio Bloco"]

# Função de limpeza e normalização
def limpar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).strip().lower()
    texto = re.sub(r"\s+", " ", texto)  # remove espaços extras
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")  # remove acentos
    return texto

# Criar versões limpas das colunas de busca
for col in colunas_busca:
    if col in df_mdu.columns:
        df_mdu[f"{col}_limpo"] = df_mdu[col].apply(limpar_texto)

# Entrada do usuário
input_busca = st.text_input("Digite o endereço, ID Smap ou nome do MDU:")

def buscar_mdu_flexivel(entrada):
    entrada_limpa = limpar_texto(entrada)
    resultados = []

    for col in colunas_busca:
        col_limpo = f"{col}_limpo"
        if col_limpo in df_mdu.columns:
            lista_opcoes = df_mdu[col_limpo].unique()
            matches = process.extract(entrada_limpa, lista_opcoes, limit=15, score_cutoff=60)
            for match, score, _ in matches:
                encontrados = df_mdu[df_mdu[col_limpo] == match]
                encontrados["Correspondência"] = f"{col} (score: {score})"
                resultados.append(encontrados)

    if resultados:
        return pd.concat(resultados, ignore_index=True)
    else:
        return pd.DataFrame()

# Executar busca
if input_busca:
    with st.spinner("🔍 Buscando MDUs..."):
        resultados = buscar_mdu_flexivel(input_busca)
        if not resultados.empty:
            st.success(f"✅ {len(resultados)} resultado(s) encontrado(s).")
            st.dataframe(resultados)
        else:
            st.warning("⚠️ Nenhum MDU encontrado com os dados fornecidos.")
