import streamlit as st
import pandas as pd
import time
import os
import requests

# Função para baixar arquivo da URL se não existir localmente
def download_base(url: str, arquivo_local: str):
    if not os.path.exists(arquivo_local):
        with st.spinner(f"⬇️ Baixando base de dados..."):
            r = requests.get(url)
            with open(arquivo_local, "wb") as f:
                f.write(r.content)
    return arquivo_local

# Exemplo URL (troque pela URL real da sua base)
URL_BASE = "https://exemplo.com/base_dados.xlsx"
ARQUIVO_BASE_LOCAL = "data/base_dados.xlsx"

# Baixar base de dados se não existir
download_base(URL_BASE, ARQUIVO_BASE_LOCAL)

# Ler base de dados
df = pd.read_excel(ARQUIVO_BASE_LOCAL, engine="openpyxl")
df = df.loc[:, ~df.columns.duplicated()]  # Remove colunas duplicadas

# Colunas essenciais
colunas_essenciais = ["POP", "CHASSI", "PLACA", "OLT", "PORTAS", "ID CTO", "CIDADE", "NOME ANTIGO CTO"]
if not all(col in df.columns for col in colunas_essenciais):
    st.error("❌ Colunas essenciais ausentes na planilha. Verifique se possui: " + ", ".join(colunas_essenciais))
    st.stop()

# Criar CAMINHO_REDE
df["CAMINHO_REDE"] = df["POP"].astype(str) + " / " + df["CHASSI"].astype(str) + " / " + df["PLACA"].astype(str) + " / " + df["OLT"].astype(str)

# Pré-calcular soma de portas por caminho de rede
portas_por_caminho = df.groupby("CAMINHO_REDE")["PORTAS"].sum().to_dict()

# Menu lateral para escolher a aba
aba = st.sidebar.radio("Selecione a aba", ["1. Visão Geral", "2. Buscar por CTO", "3. CTOs Próximas"])

if aba == "1. Visão Geral":
    with st.spinner("🔄 Carregando visão geral..."):
        progress_bar = st.progress(0)
        for i in range(5):
            time.sleep(0.1)
            progress_bar.progress((i + 1) * 20)

        total_ctos = len(df)
        total_portas = df["PORTAS"].sum()

        caminho_rede_grupo = pd.DataFrame(list(portas_por_caminho.items()), columns=["CAMINHO_REDE", "PORTAS"])
        saturados = caminho_rede_grupo[caminho_rede_grupo["PORTAS"] > 128]

    progress_bar.empty()

    st.title("📊 Verificador de Portas por Caminho de Rede")
    st.metric("🔢 Total de CTOs", total_ctos)
    st.metric("🔌 Total de Portas", total_portas)
    st.metric("🔴 Caminhos Saturados", len(saturados))

elif aba == "2. Buscar por CTO":
    # Importa o módulo da página 2 e chama a função principal
    from pages import buscar_cto
    buscar_cto.app(df)

elif aba == "3. CTOs Próximas":
    # Importa o módulo da página 3 e chama a função principal
    from pages import ctos_proximas
    ctos_proximas.app(df)
