import streamlit as st
import pandas as pd
import os
from io import BytesIO
import re

st.title("🔗 Unir POP e CTO — com tratamento para nomes já padronizados")

uploaded_file = st.file_uploader("📂 Envie a planilha com colunas 'pop' e 'cto'", type=["xlsx"])

def extrair_final_cto(row):
    pop = str(row['pop']).strip().upper()
    cto = str(row['cto']).strip().upper()

    # Verifica se já está no formato correto: POP-nnn
    if re.fullmatch(f"{pop}-\\d+", cto):
        return cto  # já padronizado, mantém
    # Caso contrário, extrai o final após o traço e padroniza
    final = cto.split('-')[-1].zfill(3)
    return f"{pop}-{final}"

def gerar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='CTO Unificadas')
    output.seek(0)
    return output

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Validação das colunas
    if 'pop' not in df.columns or 'cto' not in df.columns:
        st.error("❌ A planilha precisa ter as colunas 'pop' e 'cto'.")
    else:
        df['pop'] = df['pop'].astype(str).str.strip().str.upper()
        df['cto'] = df['cto'].astype(str).str.strip().str.upper()
        df['cto_final'] = df.apply(extrair_final_cto, axis=1)

        st.success("✅ Coluna unificada criada com sucesso!")
        st.dataframe(df[['pop', 'cto', 'cto_final']])

        st.download_button(
            label="📥 Baixar planilha com CTOs unificadas",
            data=gerar_excel(df),
            file_name="ctos_unificadas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
