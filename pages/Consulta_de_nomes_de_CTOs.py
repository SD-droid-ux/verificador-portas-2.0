import streamlit as st
import pandas as pd
import os
from io import BytesIO

st.title("🔄 Consulta de Nomes de CTOs")

# Upload do arquivo de correspondência
arquivo_corrigidos = st.file_uploader("📁 Envie a base 'base_nomes_corrigidos.xlsx'", type=["xlsx"])

# Campo para colar os nomes das CTOs
input_ctos = st.text_area("📋 Insira os nomes das CTOs (uma por linha)").upper().splitlines()
input_ctos = [cto.strip() for cto in input_ctos if cto.strip()]

def converter_para_excel(df_resultado):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_resultado.to_excel(writer, index=False, sheet_name='Correspondência CTO')
    return output.getvalue()

if arquivo_corrigidos and input_ctos:
    df_corrigidos = pd.read_excel(arquivo_corrigidos)

    # Normaliza os nomes para facilitar a busca
    df_corrigidos["cto_antigo"] = df_corrigidos["cto_antigo"].astype(str).str.upper().str.strip()
    df_corrigidos["cto_novo"] = df_corrigidos["cto_novo"].astype(str).str.upper().str.strip()

    # Filtra os dados com base nas CTOs informadas (procurando em ambas as colunas)
    df_resultado = df_corrigidos[
        df_corrigidos["cto_antigo"].isin(input_ctos) | df_corrigidos["cto_novo"].isin(input_ctos)
    ].copy()

    if df_resultado.empty:
        st.warning("⚠️ Nenhuma correspondência encontrada para os nomes informados.")
    else:
        st.success(f"✅ {len(df_resultado)} correspondência(s) encontrada(s).")
        st.dataframe(df_resultado)

        st.download_button(
            label="⬇️ Baixar Resultado em Excel",
            data=converter_para_excel(df_resultado),
            file_name="resultado_cto_correspondencias.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("📌 Envie a base corrigida e insira pelo menos um nome de CTO.")
