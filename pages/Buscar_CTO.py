import streamlit as st
import pandas as pd
import os

# Caminhos dos arquivos
caminho_corrigido = os.path.join("pages", "base_de_dados", "base_nomes_corrigidos.xlsx")
caminho_base_rede = os.path.join("pages", "base_de_dados", "base.xlsx")

st.title("🔍 Buscar CTO")

# Carrega os dados com cache para acelerar performance
@st.cache_data
def carregar_dados():
    df_corrigidos = pd.read_excel(caminho_corrigido)
    df_base = pd.read_excel(caminho_base_rede)

    # Normaliza a coluna da base
    df_base["cto"] = df_base["cto"].astype(str).str.strip().str.upper()

    # Normaliza colunas da base de nomes corrigidos
    df_corrigidos["cto_novo"] = df_corrigidos["cto_novo"].astype(str).str.strip().str.upper()
    df_corrigidos["cto_antigo"] = df_corrigidos["cto_antigo"].astype(str).str.strip().str.upper()

    # Cria dicionário para buscar nome antigo a partir do novo
    dict_novos_para_antigos = dict(zip(df_corrigidos["cto_novo"], df_corrigidos["cto_antigo"]))

    return df_base, dict_novos_para_antigos

df_base, dict_novos_para_antigos = carregar_dados()

# Entrada de CTO
entrada = st.text_input("Insira o nome da CTO (antigo ou novo):")

if st.button("🔎 Iniciar busca") and entrada:
    entrada = entrada.strip().upper()

    # Tenta buscar diretamente pela CTO
    resultado = df_base[df_base["cto"] == entrada]

    # Se não encontrou, tenta usar o nome antigo via base de correção
    if resultado.empty:
        nome_antigo = dict_novos_para_antigos.get(entrada)
        if nome_antigo:
            resultado = df_base[df_base["cto"] == nome_antigo]

    # Exibe resultados
    if not resultado.empty:
        st.success(f"{len(resultado)} resultado(s) encontrado(s):")
        st.dataframe(resultado)
    else:
        st.warning("Nenhuma informação encontrada para essa CTO.")
