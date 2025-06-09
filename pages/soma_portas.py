import streamlit as st
import pandas as pd
import os

st.title("🧮 Verificador de Portas por Caminho de Rede")

# Caminho fixo para a base existente
caminho_base_rede = os.path.join("pages", "base_de_dados", "base.xlsx")

# Upload da nova planilha de CTOs
novas_ctos_file = st.file_uploader("📥 Envie a planilha com novas CTOs a adicionar", type=["xlsx"])

if novas_ctos_file:
    # Leitura das bases
    df_atual = pd.read_excel(caminho_base_rede)
    df_novas = pd.read_excel(novas_ctos_file)

    # Padronização dos nomes das colunas
    df_atual.columns = df_atual.columns.str.lower().str.strip()
    df_novas.columns = df_novas.columns.str.lower().str.strip()

    # Colunas necessárias
    caminho_cols = ['pop', 'olt', 'slot', 'pon']
    col_portas = 'portas'

    # Verificar se todas as colunas necessárias existem
    colunas_faltando = [col for col in caminho_cols + [col_portas] if col not in df_novas.columns or col not in df_atual.columns]

    if colunas_faltando:
        st.error(f"❌ As seguintes colunas estão faltando na base: {', '.join(colunas_faltando)}")
    else:
        # Soma total de portas existentes por caminho
        df_existente = df_atual.groupby(caminho_cols)[col_portas].sum().reset_index(name='portas_existentes')

        # Soma total de portas novas por caminho
        df_novas_group = df_novas.groupby(caminho_cols)[col_portas].sum().reset_index(name='portas_novas')

        # Juntar as duas bases por caminho
        df_resultado = pd.merge(df_existente, df_novas_group, on=caminho_cols, how='outer').fillna(0)

        # Calcular total de portas e status
        df_resultado['total_apos_inclusao'] = df_resultado['portas_existentes'] + df_resultado['portas_novas']
        df_resultado['status'] = df_resultado['total_apos_inclusao'].apply(
            lambda x: "❌ Ultrapassa 128" if x > 128 else "✅ OK"
        )

        # Exibir resultado
        st.subheader("🔍 Resultado da Verificação")
        st.dataframe(df_resultado)

        # Exportar resultado
        csv = df_resultado.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Resultado em CSV", data=csv, file_name="verificacao_portas.csv", mime='text/csv')
