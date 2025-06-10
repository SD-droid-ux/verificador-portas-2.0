import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Verificador de Saturação", layout="wide")
st.title("🔌 Verificador de Saturação por Caminho de Rede")

# Upload da planilha de novas CTOs
arquivo_novo = st.file_uploader("Envie a planilha com as novas CTOs", type=["xlsx"])

# Caminho da base oficial
caminho_base = os.path.join("pages", "base_de_dados", "base.xlsx")

# Quando arquivo for enviado
if arquivo_novo:
    try:
        df_novas = pd.read_excel(arquivo_novo)

        # Garantir colunas mínimas necessárias
        colunas_necessarias = ['pop', 'olt', 'slot', 'pon', 'cto', 'portas']
        if not all(col in df_novas.columns for col in colunas_necessarias):
            st.error(f"A planilha deve conter as colunas: {colunas_necessarias}")
        else:
            # Criar coluna caminho_rede nas novas
            df_novas['caminho_rede'] = df_novas[['pop', 'olt', 'slot', 'pon']].agg('/'.join, axis=1)
            portas_novas = df_novas.groupby('caminho_rede')['portas'].sum().reset_index()
            portas_novas.rename(columns={'portas': 'portas_novas'}, inplace=True)

            # Ler base existente
            df_base = pd.read_excel(caminho_base)
            df_base['caminho_rede'] = df_base[['pop', 'olt', 'slot', 'pon']].agg('/'.join, axis=1)
            portas_existentes = df_base.groupby('caminho_rede')['portas'].sum().reset_index()
            portas_existentes.rename(columns={'portas': 'portas_existentes'}, inplace=True)

            # Combinar novas e existentes
            df_total = pd.merge(portas_existentes, portas_novas, on='caminho_rede', how='outer').fillna(0)
            df_total['portas_existentes'] = df_total['portas_existentes'].astype(int)
            df_total['portas_novas'] = df_total['portas_novas'].astype(int)
            df_total['total_final'] = df_total['portas_existentes'] + df_total['portas_novas']
            df_total['status'] = df_total['total_final'].apply(lambda x: 'ULTRAPASSOU' if x > 128 else 'OK')

            # Mostrar resultado
            st.success("Análise concluída:")
            st.dataframe(df_total[['caminho_rede', 'portas_existentes', 'portas_novas', 'total_final', 'status']],
                         use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("Por favor, envie um arquivo Excel com as novas CTOs para iniciar a verificação.")
