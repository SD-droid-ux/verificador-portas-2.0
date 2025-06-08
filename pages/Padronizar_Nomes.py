import streamlit as st
import pandas as pd
import os
from io import BytesIO

st.title("🔗 Unir POP e CTO")

uploaded_file = st.file_uploader("📂 Envie a planilha com colunas 'pop' e 'cto'", type=["xlsx"])

def extrair_final_cto(cto):
    if pd.isna(cto):
        return ""
    cto = str(cto).strip()
    if '-' in cto:
        return cto.split('-')[-1].zfill(3)  # Garante sempre 3 dígitos
    return cto.zfill(3)

def gerar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='CTO Unificadas')
    output.seek(0)
    return output

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Validação das colunas
    if 'pop' not in df.columns or 'cto' not in df.columns:
        st.error("❌ A planilha precisa ter as colunas 'pop' e 'cto'.")
    else:
        # Processamento
        df['pop'] = df['pop'].astype(str).str.strip().str.upper()
        df['cto'] = df['cto'].astype(str).str.strip().str.upper()
        df['cto_final'] = df.apply(lambda row: f"{row['pop']}-{extrair_final_cto(row['cto'])}", axis=1)

        st.success("✅ Coluna unificada criada com sucesso!")
        st.dataframe(df[['pop', 'cto', 'cto_final']])

        st.download_button(
            label="📥 Baixar planilha com CTOs unificadas",
            data=gerar_excel(df),
            file_name="ctos_unificadas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
