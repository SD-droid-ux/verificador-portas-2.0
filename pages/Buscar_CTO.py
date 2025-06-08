import streamlit as st
import pandas as pd
import os
import time
from rapidfuzz import fuzz, process

st.title("🔍 Buscar por CTO")

# Caminho da base de dados
caminho_base = os.path.join("pages", "base_de_dados", "base.xlsx")

# Carregamento da base
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

# Padronizar CTOs
def padronizar_cto(cto, pop):
    if pd.isna(cto) or pd.isna(pop):
        return cto
    final_num = cto.split("-")[-1] if "-" in cto else cto.split("/")[-1]
    final_num = final_num.zfill(3)
    if pop == "FOR":
        pop = "FLA"
    return f"{pop}{cto[:3][-2:]}-{final_num}" if len(pop) == 3 else f"{pop}-{final_num}"

df["cto_padronizada"] = df.apply(lambda row: padronizar_cto(row["cto"], row["pop"]), axis=1)

# Filtro por estado
estado = st.selectbox("Selecione o estado:", sorted(df["cid_rede"].str[:2].unique()))
df_estado = df[df["cid_rede"].str.startswith(estado)]

# Filtro por POP
pops_disponiveis = sorted(df_estado["pop"].unique())
selecionar_todos_pop = st.checkbox("Selecionar todos os POPs")
pops_selecionados = pops_disponiveis if selecionar_todos_pop else st.multiselect("Selecione o(s) POP(s):", pops_disponiveis)

df_filtrado = df_estado[df_estado["pop"].isin(pops_selecionados)] if not selecionar_todos_pop else df_estado

# Campo de entrada
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

            resultados = []

            for entrada in input_ctos:
                candidatos = df_filtrado.copy()
                candidatos["similaridade_cto"] = candidatos["cto"].apply(lambda x: fuzz.token_sort_ratio(entrada, str(x)))
                candidatos["similaridade_padronizada"] = candidatos["cto_padronizada"].apply(lambda x: fuzz.token_sort_ratio(entrada, str(x)))
                candidatos["similaridade"] = candidatos[["similaridade_cto", "similaridade_padronizada"]].max(axis=1)

                melhores = candidatos[candidatos["similaridade"] >= 85].copy()
                melhores["entrada_usuario"] = entrada
                resultados.append(melhores)

            df_resultado = pd.concat(resultados, ignore_index=True)

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

            if df_resultado.empty:
                st.info("Nenhuma CTO encontrada com correspondência suficiente.")
            else:
                df_resultado["STATUS"] = df_resultado.apply(obter_status, axis=1)
                df_resultado = df_resultado.sort_values(["entrada_usuario", "similaridade"], ascending=[True, False])
                pop_filtro_resultado = st.multiselect("Filtrar resultados por POP (opcional):", sorted(df_resultado["pop"].unique()))
                if pop_filtro_resultado:
                    df_resultado = df_resultado[df_resultado["pop"].isin(pop_filtro_resultado)]

                st.dataframe(df_resultado.reset_index(drop=True), use_container_width=True)

        progress_bar.empty()
