import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Verificador de Saturação", layout="wide")
st.title("🔌 Verificador de Saturação por Caminho de Rede")

# Upload da planilha de novas CTOs
arquivo_novo = st.file_uploader("Envie a planilha com as novas CTOs", type=["xlsx"])

# Caminho da base oficial
caminho_base = os.path.join("pages", "base_de_dados", "base.xlsx")

if arquivo_novo:
    try:
        # Leitura da nova planilha
        df_novo = pd.read_excel(arquivo_novo)
        colunas_necessarias = ['pop', 'olt', 'slot', 'pon', 'cto', 'portas']
        if not all(col in df_novo.columns for col in colunas_necessarias):
            st.error(f"A planilha deve conter as colunas: {colunas_necessarias}")
        else:
            # Criar coluna caminho_rede nas novas CTOs
            df_novo['caminho_rede'] = df_novo[['pop', 'olt', 'slot', 'pon']].astype(str).agg('/'.join, axis=1)

            # Agrupar novas por caminho de rede
            portas_novas = df_novo.groupby('caminho_rede')['portas'].sum().reset_index()
            portas_novas.rename(columns={'portas': 'portas_novas'}, inplace=True)

            # Leitura da base original
            df_base = pd.read_excel(caminho_base)
            df_base['caminho_rede'] = df_base[['pop', 'olt', 'slot', 'pon']].astype(str).agg('/'.join, axis=1)

            # Filtrar apenas os caminhos da base que aparecem na nova planilha
            caminhos_relevantes = portas_novas['caminho_rede'].unique()
            df_base_filtrado = df_base[df_base['caminho_rede'].isin(caminhos_relevantes)]

            # Agrupar base original por caminho de rede
            portas_existentes = df_base_filtrado.groupby('caminho_rede')['portas'].sum().reset_index()
            portas_existentes.rename(columns={'portas': 'portas_existentes'}, inplace=True)

            # Juntar dados
            resultado = pd.merge(portas_novas, portas_existentes, on='caminho_rede', how='left').fillna(0)
            resultado['portas_existentes'] = resultado['portas_existentes'].astype(int)
            resultado['portas_novas'] = resultado['portas_novas'].astype(int)
            resultado['total_final'] = resultado['portas_existentes'] + resultado['portas_novas']
            resultado['status'] = resultado['total_final'].apply(lambda x: 'ULTRAPASSOU' if x > 128 else 'OK')

            st.success("Resultado da análise:")
            st.dataframe(resultado, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("Envie a planilha com as novas CTOs.")
