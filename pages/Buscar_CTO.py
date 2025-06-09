import streamlit as st
import pandas as pd
import os

# Caminhos dos arquivos
caminho_corrigido = os.path.join("pages", "base_de_dados", "base_nomes_corrigidos.xlsx")
caminho_base_rede = os.path.join("pages", "base_de_dados", "base.xlsx")

st.title("🔍 Buscar CTO na Base de Dados")

# Carregamento dos dados com cache para performance
@st.cache_data
def carregar_dados():
    df_corrigidos = pd.read_excel(caminho_corrigido)
    df_base = pd.read_excel(caminho_base_rede)
    return df_corrigidos, df_base

df_corrigidos, df_base = carregar_dados()

# Criar dicionário para busca rápida dos nomes corrigidos
dict_corrigidos = dict(zip(
    df_corrigidos["cto_novo"].str.upper().str.strip(),
    df_corrigidos["cto_antigo"].str.upper().str.strip()
))

# Entrada do usuário
entrada = st.text_input("Digite o nome da CTO:", "").strip().upper()

if st.button("🔍 Buscar CTO"):
    if not entrada:
        st.warning("Por favor, digite um nome de CTO para buscar.")
    else:
        df_base["cto"] = df_base["cto"].astype(str).str.upper().str.strip()

        # 1. Buscar diretamente na base
        resultado = df_base[df_base["cto"] == entrada]

        # 2. Se não encontrar, buscar o nome antigo correspondente
        if resultado.empty and entrada in dict_corrigidos:
            cto_antiga = dict_corrigidos[entrada]
            resultado = df_base[df_base["cto"] == cto_antiga]

        if not resultado.empty:
            st.success(f"CTO encontrada ({len(resultado)} registro(s)):")
            st.dataframe(resultado)
        else:
            st.error("CTO não encontrada na base.")
