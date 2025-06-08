import streamlit as st
import pandas as pd
from io import BytesIO

st.title("🔍 Buscar Nome Antigo e Novo das CTOs")

# Upload da base de correspondências
arquivo_corrigidos = st.file_uploader("📁 Envie a base 'base_nomes_corrigidos.xlsx'", type=["xlsx"])

# Caixa de texto para inserir manualmente os nomes das CTOs
entrada = st.text_area("✍️ Insira os nomes das CTOs (uma por linha)", height=200)
lista_ctos = [cto.strip().upper() for cto in entrada.split("\n") if cto.strip()]

# Função para converter para Excel
def converter_para_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Consulta CTO')
    return output.getvalue()

if arquivo_corrigidos and lista_ctos:
    # Carrega e normaliza a base
    df_corrigidos = pd.read_excel(arquivo_corrigidos)
    df_corrigidos["cto_antigo"] = df_corrigidos["cto_antigo"].astype(str).str.strip().str.upper()
    df_corrigidos["cto_novo"] = df_corrigidos["cto_novo"].astype(str).str.strip().str.upper()

    # Filtra por correspondência direta
    df_resultado = df_corrigidos[
        df_corrigidos["cto_antigo"].isin(lista_ctos) | df_corrigidos["cto_novo"].isin(lista_ctos)
    ].copy()

    if df_resultado.empty:
        st.warning("❌ Nenhuma correspondência encontrada.")
    else:
        st.success(f"✅ {len(df_resultado)} correspondência(s) encontrada(s).")
        st.dataframe(df_resultado)

        st.download_button(
            label="⬇️ Baixar resultado em Excel",
            data=converter_para_excel(df_resultado),
            file_name="consulta_cto_nomes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
elif not arquivo_corrigidos:
    st.info("⚠️ Por favor, envie a base 'base_nomes_corrigidos.xlsx'.")
elif not lista_ctos:
    st.info("⚠️ Insira ao menos um nome de CTO para buscar.")
