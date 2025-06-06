import streamlit as st
import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2

st.title("📍 CTOs Próximas com 8 Portas e PON Disponível")

# Carrega a base de dados do repositório local
@st.cache_data
def carregar_dados():
    return pd.read_excel("base_de_dados/base.xlsx")

df = carregar_dados()

# Função para calcular a distância (em metros) entre duas coordenadas geográficas
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371000  # raio da Terra em metros
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)

    a = sin(dphi/2)**2 + cos(phi1) * cos(phi2) * sin(dlambda/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

# Cálculo de total de portas por caminho de rede
df["CAMINHO_REDE"] = df["CAMINHO_REDE"].astype(str)
portas_por_caminho = df.groupby("CAMINHO_REDE")["PORTAS"].sum().to_dict()

# Entrada da lista de CTOs NÃO trocáveis
cto_nao_trocaveis = st.text_area("Cole aqui os nomes das CTOs **NÃO trocáveis** (uma por linha)").upper().splitlines()
cto_nao_trocaveis = [cto.strip() for cto in cto_nao_trocaveis if cto.strip()]

if st.button("🔍 Buscar CTOs Próximas com 8 Portas Disponíveis"):
    if not cto_nao_trocaveis:
        st.warning("⚠️ Por favor, insira pelo menos uma CTO.")
    else:
        df_nao_trocaveis = df[df["NOME ANTIGO CTO"].isin(cto_nao_trocaveis)]
        resultados = []

        for _, linha_cto in df_nao_trocaveis.iterrows():
            lat1, lon1 = linha_cto["LAT"], linha_cto["LONG"]

            if pd.isna(lat1) or pd.isna(lon1):
                continue

            # CTOs com 8 portas e caminho com total < 128
            ctos_validas = df[
                (df["PORTAS"] == 8) &
                (df["CAMINHO_REDE"].map(portas_por_caminho) < 128) &
                (df["NOME ANTIGO CTO"] != linha_cto["NOME ANTIGO CTO"])
            ]

            for _, linha_valid in ctos_validas.iterrows():
                lat2, lon2 = linha_valid["LAT"], linha_valid["LONG"]
                if pd.isna(lat2) or pd.isna(lon2):
                    continue

                distancia = calcular_distancia(lat1, lon1, lat2, lon2)
                if distancia <= 250:
                    resultados.append({
                        "CTO BASE": linha_cto["NOME ANTIGO CTO"],
                        "CTO PRÓXIMA": linha_valid["NOME ANTIGO CTO"],
                        "CAMINHO_REDE PRÓXIMO": linha_valid["CAMINHO_REDE"],
                        "PORTAS NO CAMINHO": portas_por_caminho[linha_valid["CAMINHO_REDE"]],
                        "DISTÂNCIA (m)": round(distancia, 2)
                    })

        if resultados:
            st.success(f"✅ {len(resultados)} CTO(s) próximas encontradas.")
            st.dataframe(pd.DataFrame(resultados))
        else:
            st.info("🔎 Nenhuma CTO próxima com as condições encontradas.")
