import streamlit as st
import pandas as pd
import os

# Caminhos dos arquivos
caminho_corrigido = os.path.join("pages", "base_de_dados", "base_nomes_corrigidos.xlsx")
caminho_base_rede = os.path.join("pages", "base_de_dados", "base.xlsx")

st.title("🔍 Buscar CTO")

# Carregamento dos dados
@st.cache_data
def carregar_dados():
    df_corrigidos = pd.read_excel(caminho_corrigido)
    df_base = pd.read_excel(caminho_base_rede)
    df_base["cto"] = df_base["cto"].astype(str).str.upper().str.strip()
    return df_corrigidos, df_base

df_corrigidos, df_base = carregar_dados()

# Criar dicionário com nomes novos e antigos
dict_corrigidos = dict(zip(
    df_corrigidos["cto_novo"].str.upper().str.strip(),
    df_corrigidos["cto_antigo"].str.upper().str.strip()
))

# Entrada de CTO
entrada = st.text_input("Insira o nome da CTO que deseja buscar:")

if st.button("🔎 Iniciar busca") and entrada:
    entrada = entrada.strip().upper()

    # 1. Tenta buscar diretamente na base
    resultado = df_base[df_base["cto"] == entrada]

    # 2. Se não encontrar, busca pelo nome antigo
    if resultado.empty and entrada in dict_corrigidos:
        nome_antigo = dict_corrigidos[entrada]
        resultado = df_base[df_base["cto"] == nome_antigo]

    # Exibe resultado
    if not resultado.empty:
        st.success(f"{len(resultado)} resultado(s) encontrado(s):")
        st.dataframe(resultado)
    else:
        st.warning("Nenhum resultado encontrado para a CTO informada.")
