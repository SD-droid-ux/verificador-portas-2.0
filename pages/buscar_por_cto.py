import streamlit as st
import time
import pandas as pd

st.title("🔍 2. Buscar por CTO")

# Verifica se a base foi carregada no main.py
if "df" not in st.session_state or "portas_por_caminho" not in st.session_state:
    st.warning("⚠️ Por favor, envie a base de dados na página principal antes de usar esta funcionalidade.")
else:
    df = st.session_state["df"]
    portas_por_caminho = st.session_state["portas_por_caminho"]

    input_ctos = list(dict.fromkeys(st.text_area("Insira os ID das CTOs (uma por linha)").splitlines()))

    if st.button("🔍 Buscar CTOs"):
        with st.spinner("🔄 Analisando CTOs..."):
            progress_bar = st.progress(0)
            for i in range(5):
                time.sleep(0.1)
                progress_bar.progress((i + 1) * 20)

            df_ctos = df[df["NOME ANTIGO CTO"].isin(input_ctos)].copy()
            df_ctos["ordem"] = pd.Categorical(df_ctos["NOME ANTIGO CTO"], categories=input_ctos, ordered=True)
            df_ctos = df_ctos.sort_values("ordem").drop(columns=["ordem"])

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
