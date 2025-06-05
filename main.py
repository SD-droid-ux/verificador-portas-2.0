import streamlit as st
import pandas as pd
import time

st.title("📊 Verificador de Portas por Caminho de Rede")

uploaded_file = st.file_uploader("📂 Envie a planilha Excel", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        df = df.loc[:, ~df.columns.duplicated()]  # Remove colunas duplicadas

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

            # Aqui você chama a lógica das outras abas (Buscar por CTO, CTOs Próximas), importando seus módulos das pages

    except Exception as e:
        st.error(f"Erro ao processar a planilha: {e}")

else:
    st.info("Por favor, envie a planilha Excel para começar a análise.")
