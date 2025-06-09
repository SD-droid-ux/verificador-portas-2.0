import streamlit as st
import pandas as pd
from geopy.distance import geodesic

st.set_page_config(page_title="CTOs Próximas e Disponíveis", layout="wide")

@st.cache_data
def carregar_dados():
    df = pd.read_excel("pages/base_de_dados/base.xlsx")

    # Criar coluna CAMINHO_REDE com base em pop, olt, slot, pon
    df["CAMINHO_REDE"] = (
        df["pop"].astype(str) + "_" +
        df["olt"].astype(str) + "_" +
        df["slot"].astype(str) + "_" +
        df["pon"].astype(str)
    )

    # Converter latitude e longitude para numérico
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    # Remover coordenadas inválidas
    df = df.dropna(subset=["latitude", "longitude"])
    df = df[(df["latitude"].between(-90, 90)) & (df["longitude"].between(-180, 180))]

    return df

df = carregar_dados()

st.title("📍 Buscar CTOs Próximas e Disponíveis")

# Entrada das CTOs inválidas
cto_invalidas = st.text_area("Insira os nomes das CTOs que **NÃO podem ser trocadas** (uma por linha):")

if st.button("🔍 Buscar CTOs Disponíveis em até 250m"):
    if not cto_invalidas.strip():
        st.warning("⚠️ Por favor, insira ao menos uma CTO inválida.")
    else:
        lista_ctos_invalidas = [cto.strip().upper() for cto in cto_invalidas.splitlines() if cto.strip()]
        df["cto"] = df["cto"].astype(str).str.upper()

        # Total de portas por caminho de rede
        portas_por_caminho = df.groupby("CAMINHO_REDE")["portas"].sum().to_dict()

        # Filtrar CTOs inválidas
        df_invalidas = df[df["cto"].isin(lista_ctos_invalidas)].copy()

        # CTOs candidatas (8 portas e caminho < 128)
        df_candidatas = df[df["portas"] == 8].copy()
        df_candidatas["TOTAL_PORTAS_CAMINHO"] = df_candidatas["CAMINHO_REDE"].map(portas_por_caminho)
        df_candidatas = df_candidatas[df_candidatas["TOTAL_PORTAS_CAMINHO"] < 128]

        resultados = []

        # Busca de CTOs próximas
        for _, inv in df_invalidas.iterrows():
            coord_inv = (inv["latitude"], inv["longitude"])
            nome_cto_inv = inv["cto"]

            for _, cand in df_candidatas.iterrows():
                coord_cand = (cand["latitude"], cand["longitude"])
                distancia = geodesic(coord_inv, coord_cand).meters
                if distancia <= 200:
                    cand_copy = cand.copy()
                    cand_copy["possível_troca"] = f"{nome_cto_inv}  --->  {cand_copy['cto']}"
                    resultados.append(cand_copy)

        if resultados:
            df_resultado = pd.DataFrame(resultados).drop_duplicates(subset=["cto"])
            st.success(f"✅ Foram encontradas {len(df_resultado)} CTOs disponíveis a até 250m das CTOs inválidas.")

            cidade_filtro = st.selectbox("Filtrar por cidade (opcional):", options=["Todas"] + sorted(df_resultado["cid_rede"].unique().tolist()))
            if cidade_filtro != "Todas":
                df_resultado = df_resultado[df_resultado["cid_rede"] == cidade_filtro]

            st.dataframe(df_resultado[["cto", "cid_rede", "latitude", "longitude", "TOTAL_PORTAS_CAMINHO", "possível_troca"]])
        else:
            st.info("Nenhuma CTO com 8 portas e caminho < 128 encontrada a até 250m das CTOs inválidas.")
