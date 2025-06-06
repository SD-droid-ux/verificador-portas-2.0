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

    # Converter LAT e LONG para numérico, valores inválidos virarão NaN
    df["LAT"] = pd.to_numeric(df["LAT"], errors="coerce")
    df["LONG"] = pd.to_numeric(df["LONG"], errors="coerce")

    # Remover linhas com NaN em LAT ou LONG
    df = df.dropna(subset=["LAT", "LONG"])

    # Remover latitudes fora do intervalo válido [-90, 90]
    df = df[(df["LAT"] >= -90) & (df["LAT"] <= 90)]

    # Remover longitudes fora do intervalo válido [-180, 180]
    df = df[(df["LONG"] >= -180) & (df["LONG"] <= 180)]

    return df

df = carregar_dados()

# Mostrar possíveis dados inválidos para debug (pode remover depois)
df_invalid_lat = df[(df["LAT"] < -90) | (df["LAT"] > 90)]
df_invalid_long = df[(df["LONG"] < -180) | (df["LONG"] > 180)]

if not df_invalid_lat.empty or not df_invalid_long.empty:
    st.warning("⚠️ Existem dados com coordenadas inválidas que foram removidos.")

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

        proximas = []

        for _, row_inv in df_invalidas.iterrows():
            lat_inv, long_inv = row_inv["LAT"], row_inv["LONG"]
            for _, row_cand in df_candidatas.iterrows():
                lat_cand, long_cand = row_cand["LAT"], row_cand["LONG"]

                # Se alguma coordenada for inválida, ignora (proteção extra)
                if not (-90 <= lat_inv <= 90 and -180 <= long_inv <= 180):
                    continue
                if not (-90 <= lat_cand <= 90 and -180 <= long_cand <= 180):
                    continue

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
