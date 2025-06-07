import streamlit as st
import pandas as pd
import os
from rapidfuzz import process, fuzz

st.title("🏢 Buscador de MDUs")

# Caminho da base de dados
caminho_mdu = os.path.join("pages", "base_de_dados", "base_mdu.xlsx")
caminho_cto = os.path.join("pages", "base_de_dados", "base.xlsx")  # base com CTOs ativas

# Carregar bases
try:
    df_mdu = pd.read_excel(caminho_mdu)
    df_cto = pd.read_excel(caminho_cto)
except FileNotFoundError:
    st.warning("⚠️ Base de dados não encontrada. Por favor, envie na página principal.")
    st.stop()

# Input de busca
input_busca = st.text_input("🔍 Digite parte do endereço, nome do condomínio, SMAP ou ID SMAP").strip()

def buscar_mdu_flexivel(valor):
    """Busca aproximada nos campos relevantes da base de MDUs"""
    colunas_chave = ["Endereço", "Nome do Condomínio Bloco", "Smap(Projetos)", "ID Smap"]
    resultados = pd.DataFrame()
    for col in colunas_chave:
        similares = process.extract(
            query=valor,
            choices=df_mdu[col].astype(str).unique(),
            scorer=fuzz.token_sort_ratio,
            limit=10
        )
        encontrados = [item[0] for item in similares if item[1] >= 70]
        filtrado = df_mdu[df_mdu[col].astype(str).isin(encontrados)]
        resultados = pd.concat([resultados, filtrado], ignore_index=True)
    return resultados.drop_duplicates()

# Processa busca
if input_busca:
    mdu_resultados = buscar_mdu_flexivel(input_busca)

    if mdu_resultados.empty:
        st.error("Nenhum MDU encontrado com os critérios informados.")
    else:
        st.success(f"🔎 {len(mdu_resultados)} MDU(s) encontrados.")
        for idx, row in mdu_resultados.iterrows():
            nome = row["Nome do Condomínio Bloco"]
            endereco = row["Endereço"]
            smap = row["Smap(Projetos)"]
            id_smap = row["ID Smap"]

            st.markdown(f"### 🏢 {nome or '(sem nome)'}")
            st.markdown(f"📍 **Endereço:** {endereco}")
            st.markdown(f"🆔 **SMAP:** {smap} | **ID SMAP:** {id_smap}")

            # Filtra CTOs por endereço aproximado ou nome do condomínio
            df_ctos_mdu = df_cto[
                df_cto["cto"].notnull() &
                (
                    df_cto["cto"].str.contains(nome, case=False, na=False) |
                    df_cto["cto"].str.contains(endereco, case=False, na=False)
                )
            ].copy()

            if not df_ctos_mdu.empty:
                st.markdown("✅ **MDU ADEQUADO**")
                df_ctos_mdu["ocupadas"] = df_ctos_mdu["portas"] - df_ctos_mdu["portas"].where(df_ctos_mdu["portas"] < 128, 128)
                df_ctos_mdu["livres"] = df_ctos_mdu["portas"] - df_ctos_mdu["ocupadas"]
                df_ctos_mdu["saturacao (%)"] = round(100 * df_ctos_mdu["ocupadas"] / df_ctos_mdu["portas"], 1)

                st.dataframe(df_ctos_mdu[["cto", "portas", "ocupadas", "livres", "saturacao (%)"]])
            else:
                # Verifica se foi projetado
                if pd.notna(smap) or pd.notna(id_smap):
                    st.warning("⚠️ **MDU PROJETADO MAS NÃO ADEQUADO** — ainda sem CTO ativa.")
                else:
                    st.error("❌ **MDU NÃO PROJETADO** — não há informações suficientes.")
