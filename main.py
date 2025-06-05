import streamlit as st
import pandas as pd
import time

st.set_page_config(layout="wide")
st.title("📊 Verificador de Portas por Caminho de Rede")

uploaded_file = st.file_uploader("📂 Envie a planilha Excel", type=[".xlsx"])

if uploaded_file:
    # Leitura otimizada (carregando apenas colunas únicas e usando openpyxl)
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    df = df.loc[:, ~df.columns.duplicated()]

    colunas_essenciais = ["POP", "CHASSI", "PLACA", "OLT", "PORTAS", "ID CTO", "CIDADE", "NOME ANTIGO CTO"]
    if not all(col in df.columns for col in colunas_essenciais):
        st.error("❌ Colunas essenciais ausentes na planilha. Verifique se possui: " + ", ".join(colunas_essenciais))
    else:
        # Criar CAMINHO_REDE
        df["CAMINHO_REDE"] = df["POP"].astype(str) + " / " + df["CHASSI"].astype(str) + " / " + df["PLACA"].astype(str) + " / " + df["OLT"].astype(str)

        # Pré-calcular soma de portas por caminho de rede
        portas_por_caminho = df.groupby("CAMINHO_REDE")["PORTAS"].sum().to_dict()

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

            st.metric("🔢 Total de CTOs", total_ctos)
            st.metric("🔌 Total de Portas", total_portas)
            st.metric("🔴 Caminhos Saturados", len(saturados))

        elif aba == "2. Buscar por CTO":
            input_ctos = list(dict.fromkeys(st.text_area("Insira os ID das CTOs (uma por linha)").splitlines()))

            if st.button("🔍 Buscar CTOs"):
                with st.spinner("🔄 Analisando CTOs..."):
                    progress_bar = st.progress(0)
                    for i in range(5):
                        time.sleep(0.1)
                        progress_bar.progress((i + 1) * 20)

                    df_ctos = df[df["NOME ANTIGO CTO"].isin(input_ctos)]
                    df_ctos["ordem"] = pd.Categorical(df_ctos["NOME ANTIGO CTO"], categories=input_ctos, ordered=True)
                    df_ctos = df_ctos.sort_values("ordem")
                    df_ctos = df_ctos.drop(columns=["ordem"])

                    def obter_status(row):
                        total = portas_por_caminho.get(row["CAMINHO_REDE"], 0)
                        if total > 128:
                            return "🔴 Saturado"
                        elif total == 128:
                            return "🟡 Caminho de Rede já é 128"
                        elif row["PORTAS"] == 16:
                            return "⚠️ 16 portas (fora padrão)"
                        else:
                            return "✅ OK"

                    df_ctos["STATUS"] = df_ctos.apply(obter_status, axis=1)
                    st.dataframe(df_ctos)

                progress_bar.empty()

        elif aba == "3. CTOs Próximas":
            st.subheader("📍 CTOs Próximas de CTOs Saturadas")
            input_ctos_saturadas = st.text_area("Insira os nomes das CTOs Saturadas (uma por linha)").splitlines()

            if st.button("🔍 Buscar CTOs próximas"):
                with st.spinner("🔄 Processando..."):
                    df_saturadas = df[df["NOME ANTIGO CTO"].isin(input_ctos_saturadas)]
                    df_ok = df[(df["PORTAS"] == 8)]

                    # Precisamos da função geopy
                    from geopy.distance import geodesic
                    
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

                    resultados = []

                    for _, cto_sat in df_saturadas.iterrows():
                        coord_sat = (cto_sat["LAT"], cto_sat["LONG"])
                        for _, cto_ok in df_ok.iterrows():
                            coord_ok = (cto_ok["LAT"], cto_ok["LONG"])
                            distancia = geodesic(coord_sat, coord_ok).meters

                            total_portas_ok = portas_por_caminho.get(cto_ok["CAMINHO_REDE"], 0)
                            status_ok = "✅ OK" if total_portas_ok < 128 else "🔴 Saturado"

                            if distancia <= 500 and status_ok == "✅ OK":
                                resultados.append({
                                    "CTO Saturada": cto_sat["NOME ANTIGO CTO"],
                                    "CTO OK": cto_ok["NOME ANTIGO CTO"],
                                    "Distância (m)": round(distancia, 2),
                                    "Raio": "100m" if distancia <= 100 else ("300m" if distancia <= 300 else "500m"),
                                    "CAMINHO_REDE": cto_ok["CAMINHO_REDE"],
                                    "LAT": cto_ok["LAT"],
                                    "LONG": cto_ok["LONG"]
                                })

                    if resultados:
                        resultado_df = pd.DataFrame(resultados)
                        st.map(resultado_df[["LAT", "LONG"]])
                        st.dataframe(resultado_df)
                    else:
                        st.warning("❌ Nenhuma CTO próxima com 8 portas e status OK encontrada.")

else:
    st.info("📥 Aguarde o envio de um arquivo para iniciar a análise.")
