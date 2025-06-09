import streamlit as st
import pandas as pd
import os

# Caminho da base já existente
caminho_base_rede = os.path.join("pages", "base_de_dados", "base.xlsx")

st.title("⚙️ Verificador de Portas por Caminho de Rede")

# Upload da planilha com novas CTOs
uploaded_file = st.file_uploader("📥 Envie a planilha com novas CTOs e portas", type=["xlsx"])

if uploaded_file:
    # Leitura da planilha nova
    df_novas = pd.read_excel(uploaded_file)
    df_novas.columns = df_novas.columns.str.lower().str.strip()
    
    # Lê base já existente
    df_base = pd.read_excel(caminho_base_rede)
    df_base.columns = df_base.columns.str.lower().str.strip()

    # Checagem colunas necessárias
    col_caminho = ['pop', 'olt', 'slot', 'pon']
    if not all(col in df_novas.columns for col in col_caminho + ['portas']):
        st.error(f"❌ Planilha de novas CTOs precisa conter colunas: {', '.join(col_caminho + ['portas'])}")
    elif not all(col in df_base.columns for col in col_caminho + ['portas']):
        st.error(f"❌ Base existente precisa conter colunas: {', '.join(col_caminho + ['portas'])}")
    else:
        # Agrupa portas novas por caminho de rede
        portas_novas = df_novas.groupby(col_caminho)['portas'].sum().reset_index(name='portas_novas')
        # Agrupa portas da base existente
        portas_base = df_base.groupby(col_caminho)['portas'].sum().reset_index(name='portas_base')
        
        # Faz merge para comparar
        df_comparacao = pd.merge(portas_base, portas_novas, on=col_caminho, how='outer').fillna(0)

        # Soma portas total
        df_comparacao['portas_total'] = df_comparacao['portas_base'] + df_comparacao['portas_novas']

        # Verifica ultrapassagem de limite 128 portas
        df_comparacao['status'] = df_comparacao['portas_total'].apply(
            lambda x: "❌ Ultrapassa limite (128 portas)" if x > 128 else "✅ Dentro do limite"
        )

        st.subheader("📊 Resultado da Verificação")

        st.dataframe(df_comparacao)

        # Botão para baixar o resultado
        csv = df_comparacao.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Resultado", data=csv, file_name="verificacao_portas.csv", mime="text/csv")
