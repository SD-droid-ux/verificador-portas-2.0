import streamlit as st
import pandas as pd

st.title("🔗 Agrupador de Caminhos de Rede")

# Upload da planilha com múltiplas CTOs
uploaded_file = st.file_uploader("📥 Envie a planilha com múltiplas CTOs", type=["xlsx"])

if uploaded_file:
    # Leitura e padronização da planilha
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.lower().str.strip()

    # Verifica se colunas esperadas existem
    caminho_cols = ['pop', 'olt', 'slot', 'pon']
    if not all(col in df.columns for col in caminho_cols):
        st.error(f"❌ A planilha precisa conter as colunas: {', '.join(caminho_cols)}")
    else:
        # Agrupar os caminhos de rede
        st.subheader("🔍 Visualização por Caminho de Rede")

        caminhos_unicos = df[caminho_cols].drop_duplicates()

        for _, row in caminhos_unicos.iterrows():
            filtro = (df['pop'] == row['pop']) & \
                     (df['olt'] == row['olt']) & \
                     (df['slot'] == row['slot']) & \
                     (df['pon'] == row['pon'])

            grupo = df[filtro]
            st.markdown(f"### 🔸 Caminho: {row['pop']} / {row['olt']} / {row['slot']} / {row['pon']}")
            st.dataframe(grupo)

        # Botão para exportar agrupamento completo
        csv = df.sort_values(by=caminho_cols).to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Agrupamento Completo", data=csv, file_name="agrupamento_caminhos.csv", mime="text/csv")
