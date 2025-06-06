import streamlit as st
import time
import pandas as pd

st.title("🔍 2. Buscar por CTO")

# Confere se a base já foi carregada no main.py
if "df" not in st.session_state or "portas_por_caminho" not in st.session_state:
    st.warning("⚠️ Por favor, envie a base de dados na página principal antes de usar esta funcionalidade.")
else:
    df = st.session_state["df"]
    portas_por_caminho = st.session_state["portas_por_caminho"]

    input_ctos = list(dict.fromkeys(st.text_area("Insira os ID das CTOs (uma por linha)").upper().splitlines()))
    # Upper para garantir uniformidade na busca, se necessário

    if st.button("🔍 Buscar CTOs"):
        if not input_ctos or all(not cto.strip() for cto in input_ctos):
            st.warning("⚠️ Insira pelo menos um ID de CTO para buscar.")
        else:
            with st.spinner("🔄 Analisando CTOs..."):
                progress_bar = st.progress(0)
                for i in range(5):
                    time.sleep(0.1)
                    progress_bar.progress((i + 1) * 20)

                df_ctos = df[df["NOME ANTIGO CTO"].str.upper().isin(input_ctos)].copy()
                df_ctos["ordem"] = pd.Categorical(df_ctos["NOME ANTIGO CTO"].str.upper(), categories=input_ctos, ordered=True)
                df_ctos = df_ctos.sort_values("ordem").drop(columns=["ordem"])

                def obter_status(row):
                    total = portas_por_caminho.get(row["CAMINHO_REDE"], 0)
                    if total > 128:
                        return "🔴 SATURADO"
                    elif total == 128 and row["PORTAS"] == 16:
                        return "🔴 SATURADO"
                    elif total == 128 and row["PORTAS"] == 8:
                        return "🔴 CTO É SP8 MAS PON JÁ ESTÁ SATURADA"
                    elif row["PORTAS"] == 16 and total < 128:
                        return "✅ CTO JÁ É SP16 MAS A PON NÃO ESTÁ SATURADA"
                    elif row["PORTAS"] == 8 and total < 128:
                        return "✅ TROCA DE SP8 PARA SP16"
                    else:
                        return "⚪ STATUS INDEFINIDO"

                df_ctos["STATUS"] = df_ctos.apply(obter_status, axis=1)

                if df_ctos.empty:
                    st.info("Nenhuma CTO encontrada para os IDs informados.")
                else:
                    st.dataframe(df_ctos)

            progress_bar.empty()
