import streamlit as st
import time
import pandas as pd
import os

st.title("🔍 Buscar por CTO")

# Caminho da base de dados
caminho_base = os.path.join("pages", "base_de_dados", "base.xlsx")

# Tenta carregar os dados, se não estiverem no session_state
if "df" not in st.session_state or "portas_por_caminho" not in st.session_state:
    try:
        df = pd.read_excel(caminho_base)
        df["CAMINHO_REDE"] = df["pop"].astype(str) + "/" + df["olt"].astype(str) + "/" + df["slot"].astype(str) + "/" + df["pon"].astype(str)
        portas_por_caminho = df.groupby("CAMINHO_REDE")["portas"].sum().to_dict()
        st.session_state["df"] = df
        st.session_state["portas_por_caminho"] = portas_por_caminho
    except FileNotFoundError:
        st.warning("⚠️ A base de dados não foi encontrada. Por favor, envie na página principal.")
        st.stop()

# Recupera os dados do session_state
df = st.session_state["df"]
portas_por_caminho = st.session_state["portas_por_caminho"]

input_ctos = list(dict.fromkeys(st.text_area("Insira os ID das CTOs (uma por linha)").upper().splitlines()))

if st.button("🔍 Buscar CTOs"):
    if not input_ctos or all(not cto.strip() for cto in input_ctos):
        st.warning("⚠️ Insira pelo menos um ID de CTO para buscar.")
    else:
        with st.spinner("🔄 Analisando CTOs..."):
            progress_bar = st.progress(0)
            for i in range(5):
                time.sleep(0.1)
                progress_bar.progress((i + 1) * 20)

            df_ctos = df[df["cto"].str.upper().isin(input_ctos)].copy()
            df_ctos["ordem"] = pd.Categorical(df_ctos["cto"].str.upper(), categories=input_ctos, ordered=True)
            df_ctos = df_ctos.sort_values("ordem").drop(columns=["ordem"])

            def obter_status(row):
                total = portas_por_caminho.get(row["CAMINHO_REDE"], 0)
                if total > 128:
                    return "🔴 SATURADO"
                elif total == 128 and row["portas"] == 16:
                    return "🔴 SATURADO"
                elif total == 128 and row["portas"] == 8:
                    return "🔴 CTO É SP8 MAS PON JÁ ESTÁ SATURADA"
                elif row["portas"] == 16 and total < 128:
                    return "✅ CTO JÁ É SP16 MAS A PON NÃO ESTÁ SATURADA"
                elif row["portas"] == 8 and total < 128:
                    return "✅ TROCA DE SP8 PARA SP16"
                else:
                    return "⚪ STATUS INDEFINIDO"

            df_ctos["STATUS"] = df_ctos.apply(obter_status, axis=1)

            if df_ctos.empty:
                st.info("Nenhuma CTO encontrada para os IDs informados.")
            else:
                st.dataframe(df_ctos)

        progress_bar.empty()
