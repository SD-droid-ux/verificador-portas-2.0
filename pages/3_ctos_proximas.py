import streamlit as st
import pandas as pd
from geopy.distance import geodesic

def aba_ctos_proximas(df_base):
    st.header("3. CTOs Próximas")

    # Filtro por cidade antes de qualquer processamento
    cidades_disponiveis = sorted(df_base["CIDADE"].dropna().unique())
    cidade_selecionada = st.selectbox("Selecione a cidade para análise:", cidades_disponiveis)

    if not cidade_selecionada:
        st.warning("Selecione uma cidade para continuar.")
        return

    # Filtrar dados pela cidade escolhida
    df_filtrado = df_base[df_base["CIDADE"] == cidade_selecionada]

    # Entrada das CTOs saturadas
    ctos_input = st.text_area("Insira a lista de CTOs saturadas (uma por linha):")
    if not ctos_input.strip():
        return

    lista_ctos = [cto.strip().upper() for cto in ctos_input.split("\n") if cto.strip()]
    df_saturadas = df_filtrado[df_filtrado["CTO"].isin(lista_ctos)].copy()
    df_ok = df_filtrado[(df_filtrado["STATUS"] == "OK") & (df_filtrado["PORTAS"] == 8)].copy()

    # Converter coordenadas para numérico
    df_saturadas["LAT"] = pd.to_numeric(df_saturadas["LAT"], errors="coerce")
    df_saturadas["LONG"] = pd.to_numeric(df_saturadas["LONG"], errors="coerce")
    df_ok["LAT"] = pd.to_numeric(df_ok["LAT"], errors="coerce")
    df_ok["LONG"] = pd.to_numeric(df_ok["LONG"], errors="coerce")

    # Remover coordenadas ausentes ou fora do intervalo geográfico válido
    df_saturadas = df_saturadas[
        df_saturadas["LAT"].between(-90, 90) & df_saturadas["LONG"].between(-180, 180)
    ]
    df_ok = df_ok[
        df_ok["LAT"].between(-90, 90) & df_ok["LONG"].between(-180, 180)
    ]

    # Calcular distâncias e encontrar CTOs próximas
    resultado = []
    for _, row_sat in df_saturadas.iterrows():
        coord_sat = (row_sat["LAT"], row_sat["LONG"])
        for _, row_ok in df_ok.iterrows():
            coord_ok = (row_ok["LAT"], row_ok["LONG"])
            distancia = geodesic(coord_sat, coord_ok).meters
            if distancia <= 500:
                resultado.append({
                    "CTO_SATURADA": row_sat["CTO"],
                    "CTO_OK": row_ok["CTO"],
                    "DISTÂNCIA_m": round(distancia, 2),
                    "RAIO": f"{'100m' if distancia <= 100 else '300m' if distancia <= 300 else '500m'}",
                    "CIDADE": cidade_selecionada,
                    "LAT": row_ok["LAT"],
                    "LONG": row_ok["LONG"]
                })

    if resultado:
        resultado_df = pd.DataFrame(resultado)
        st.success(f"{len(resultado_df)} CTOs próximas encontradas.")
        st.dataframe(resultado_df)

        # Exibir mapa com apenas pontos válidos
        st.map(resultado_df[["LAT", "LONG"]].dropna())
    else:
        st.warning("Nenhuma CTO próxima encontrada dentro do raio de 500 metros.")
