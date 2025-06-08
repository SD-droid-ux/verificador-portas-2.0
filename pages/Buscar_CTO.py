import streamlit as st
import time
import pandas as pd
import os
from rapidfuzz import process

st.title("🔍 Buscar por CTO")

# Caminho da base de dados
caminho_base = os.path.join("pages", "base_de_dados", "base.xlsx")

# Carrega a base no session_state, se necessário
if "df" not in st.session_state or "portas_por_caminho" not in st.session_state:
    try:
        df = pd.read_excel(caminho_base)
        df["CAMINHO_REDE"] = df["pop"].astype(str) + "/" + df["olt"].astype(str) + "/" + df["slot"].astype(str) + "/" + df["pon"].astype(str)
        portas_por_caminho = df.groupby("CAMINHO_REDE")["portas"].sum().to_dict()
        st.session_state["df"] = df
        st.session_state["portas_por_caminho"] = portas_por_caminho
    except FileNotFoundError:
        st.warning("⚠️ A base de dados não foi encontrada.")
        st.stop()

# Recupera do session_state
df = st.session_state["df"]
portas_por_caminho = st.session_state["portas_por_caminho"]

# Filtro por estado
todos_estados = st.checkbox("🔄 Buscar em TODOS os Estados", value=False)

if todos_estados:
    df_filtrado_estado = df.copy()
else:
    estado_selecionado = st.selectbox("📍 Selecione o Estado", sorted(df["estado"].dropna().unique()))
    df_filtrado_estado = df[df["estado"] == estado_selecionado]

# Filtro por POP
todos_pops = st.checkbox("🔄 Buscar em TODOS os POPs do estado selecionado", value=False)

if todos_pops:
    df_filtrado = df_filtrado_estado.copy()
else:
    pops_disponiveis = sorted(df_filtrado_estado["pop"].dropna().unique())
    pop_selecionado = st.selectbox("📡 Selecione o POP", pops_disponiveis)
    df_filtrado = df_filtrado_estado[df_filtrado_estado["pop"] == pop_selecionado]

# Entrada de CTOs
input_ctos = list(dict.fromkeys(st.text_area("✏️ Insira os ID das CTOs (uma por linha)").upper().splitlines()))

def buscar_com_correspondencia(cto_input, lista_ctos_base, limite=80):
    correspondencias = process.extract(
        query=cto_input,
        choices=lista_ctos_base,
        score_cutoff=limite,
        limit=5
    )
    return correspondencias

if st.button("🔍 Buscar CTOs"):
    if not input_ctos or all(not cto.strip() for cto in input_ctos):
        st.warning("⚠️ Insira pelo menos um ID de CTO.")
    else:
        with st.spinner("🔄 Buscando correspondências..."):
            resultados_finais = []

            lista_ctos_base = df_filtrado["cto"].dropna().astype(str).str.upper().unique().tolist()

            for cto in input_ctos:
                correspondencias = buscar_com_correspondencia(cto, lista_ctos_base)
                for cto_encontrada, score, _ in correspondencias:
                    dados_cto = df_filtrado[df_filtrado["cto"].str.upper() == cto_encontrada].copy()
                    dados_cto["SCORE"] = score
                    resultados_finais.append(dados_cto)

            if not resultados_finais:
                st.info("Nenhuma correspondência encontrada.")
            else:
                df_resultado = pd.concat(resultados_finais).drop_duplicates().sort_values(by="SCORE", ascending=False)

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

                df_resultado["STATUS"] = df_resultado.apply(obter_status, axis=1)
                st.success(f"✅ {len(df_resultado)} correspondência(s) encontradas.")
                st.dataframe(df_resultado)
