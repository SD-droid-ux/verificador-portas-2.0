import streamlit as st
import pandas as pd
from geopy.distance import geodesic

st.set_page_config(page_title="CTOs Próximas e Disponíveis", layout="wide")

@st.cache_data
def carregar_dados():
    df = pd.read_excel("pages/base_de_dados/base.xlsx")

    # Criar coluna CAMINHO_REDE com base em POP, CHASSI, PLACA, OLT
    df["CAMINHO_REDE"] = (
        df["POP"].astype(str) + "_" +
        df["CHASSI"].astype(str) + "_" +
        df["PLACA"].astype(str) + "_" +
        df["OLT"].astype(str)
    )

        df["LAT"] = pd.to_numeric(df["LAT"], errors="coerce")
        df["LONG"] = pd.to_numeric(df["LONG"], errors="coerce")

        # Remove linhas com LAT ou LONG inválidas
        df = df.dropna(subset=["LAT", "LONG"])

    return df

df = carregar_dados()

st.title("📍 Buscar CTOs Próximas e Disponíveis")

# Entrada da lista de CTOs que NÃO podem ser trocadas
cto_invalidas = st.text_area("Insira os nomes das CTOs que **NÃO podem ser trocadas** (uma por linha):")

if st.button("🔍 Buscar CTOs Disponíveis em até 250m"):
    if not cto_invalidas.strip():
        st.warning("⚠️ Por favor, insira ao menos uma CTO inválida.")
    else:
        lista_ctos_invalidas = [cto.strip().upper() for cto in cto_invalidas.splitlines() if cto.strip()]
        df["NOME ANTIGO CTO"] = df["NOME ANTIGO CTO"].astype(str).str.upper()

        # Criar dicionário com total de portas por caminho
        portas_por_caminho = df.groupby("CAMINHO_REDE")["PORTAS"].sum().to_dict()

        # CTOs inválidas (de entrada)
        df_invalidas = df[df["NOME ANTIGO CTO"].isin(lista_ctos_invalidas)].copy()

        # CTOs candidatas (8 portas e caminho com < 128 portas)
        df_candidatas = df[(df["PORTAS"] == 8)].copy()
        df_candidatas["TOTAL_PORTAS_CAMINHO"] = df_candidatas["CAMINHO_REDE"].map(portas_por_caminho)
        df_candidatas = df_candidatas[df_candidatas["TOTAL_PORTAS_CAMINHO"] < 128]

        # Lista para armazenar CTOs próximas
        proximas = []

        for _, row_inv in df_invalidas.iterrows():
            lat_inv, long_inv = row_inv["LAT"], row_inv["LONG"]
            for _, row_cand in df_candidatas.iterrows():
                lat_cand, long_cand = row_cand["LAT"], row_cand["LONG"]
                distancia = geodesic((lat_inv, long_inv), (lat_cand, long_cand)).meters
                if distancia <= 250:
                    proximas.append(row_cand)

        if proximas:
            df_resultado = pd.DataFrame(proximas).drop_duplicates(subset=["NOME ANTIGO CTO"])
            st.success(f"✅ Foram encontradas {len(df_resultado)} CTOs disponíveis a até 250m das CTOs inválidas.")
            cidade_filtro = st.selectbox("Filtrar por cidade (opcional):", options=["Todas"] + sorted(df_resultado["CIDADE"].unique().tolist()))
            if cidade_filtro != "Todas":
                df_resultado = df_resultado[df_resultado["CIDADE"] == cidade_filtro]
            st.dataframe(df_resultado)
        else:
            st.info("Nenhuma CTO com 8 portas e caminho < 128 encontrada a até 250m das CTOs inválidas.")
