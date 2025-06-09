import streamlit as st
import pandas as pd
import os

st.title("🧮 Verificador de Caminhos de Rede - Capacidade de Portas")

# Caminhos fixos
caminho_base_rede = os.path.join("pages", "base_de_dados", "base.xlsx")

# Upload da nova base
novas_ctos_file = st.file_uploader("📥 Envie a planilha com novas CTOs a adicionar", type=["xlsx"])

if novas_ctos_file:
    # Carregar os dados
    df_atual = pd.read_excel(caminho_base_rede)
    df_novas = pd.read_excel(novas_ctos_file)

    # Padronizar colunas
    colunas_padrao = ['pop', 'olt', 'slot', 'pon', 'cto', 'portas']
    df_atual.columns = df_atual.columns.str.lower().str.strip()
    df_novas.columns = df_novas.columns.str.lower().str.strip()

    df_atual = df_atual[[col for col in colunas_padrao if col in df_atual.columns]]
    df_novas = df_novas[[col for col in colunas_padrao if col in df_novas.columns]]

    # Agrupar por caminho de rede
    grupo_cols = ['pop', 'olt', 'slot', 'pon']
    atual_group = df_atual.groupby(grupo_cols)['portas'].sum().reset_index(name='portas_existentes')
    novas_group = df_novas.groupby(grupo_cols)['portas'].sum().reset_index(name='portas_novas')

    # Verificar capacidade
    df_resultado = pd.merge(atual_group, novas_group, on=grupo_cols, how='outer').fillna(0)
    df_resultado['total_apos_inclusao'] = df_resultado['portas_existentes'] + df_resultado['portas_novas']
    df_resultado['status'] = df_resultado['total_apos_inclusao'].apply(lambda x: "❌ Ultrapassa 128" if x > 128 else "✅ OK")

    st.subheader("🔎 Resultado da Verificação")
    st.dataframe(df_resultado)

    # Botão para exportar os resultados
    csv = df_resultado.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 Baixar resultado em CSV", data=csv, file_name="resultado_verificacao_portas.csv", mime='text/csv')
