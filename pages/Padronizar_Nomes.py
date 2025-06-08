import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.title("🔧 Padronizar Nome das CTOs")

uploaded_file = st.file_uploader("📤 Envie a planilha com os dados (POP e CTO)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Verificação de colunas obrigatórias
    if 'pop' not in df.columns or 'cto' not in df.columns:
        st.error("A planilha deve conter as colunas: 'pop' e 'cto'")
        st.stop()

    def corrigir_nome_cto(pop, cto):
        # Regra 1: mudar 'FOR' para 'FLA'
        if pop.startswith("FOR"):
            pop_corrigido = pop.replace("FOR", "FLA", 1)
        else:
            pop_corrigido = pop

        # Extrair final numérico da CTO (último grupo de dígitos)
        match = re.search(r'(\d{2,3})$', cto)
        if not match:
            return f"{pop_corrigido}-{cto}"  # fallback, sem alteração numérica
        numero = match.group(1)

        cto_corrigido = f"{pop_corrigido}-{numero}"

        # Regra 3: se o nome já estiver correto, mantém
        if cto_corrigido == cto:
            return cto

        return cto_corrigido

    df["cto_corrigida"] = df.apply(lambda row: corrigir_nome_cto(str(row["pop"]).strip(), str(row["cto"]).strip()), axis=1)

    st.success("✅ CTOs corrigidas com sucesso!")
    st.dataframe(df)

    # Download do arquivo corrigido
    def converter_para_excel(df):
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="CTOs Corrigidas")
        buffer.seek(0)
        return buffer

    st.download_button(
        label="📥 Baixar Excel com CTOs Corrigidas",
        data=converter_para_excel(df),
        file_name="ctos_corrigidas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
