import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Buscar CTO", layout="wide")

# Caminhos dos arquivos
caminho_corrigido = os.path.join("pages", "base_de_dados", "base_nomes_corrigidos.xlsx")
caminho_base_rede = os.path.join("pages", "base_de_dados", "base.xlsx")

# Cache das bases
@st.cache_data(show_spinner=False)
def carregar_dados():
    df_corrigidos = pd.read_excel(caminho_corrigido)
    df_base = pd.read_excel(caminho_base_rede)
    return df_corrigidos, df_base

df_corrigidos, df_base = carregar_dados()

# Criar dicionário nome_corrigido -> nome_antigo para busca rápida
dict_corrigidos = dict(zip(df_corrigidos["nome_corrigido"].str.upper().str.strip(),
                           df_corrigidos["nome_antigo"].str.upper().str.strip()))

st.title("🔎 Buscar Informações da CTO")
st.write("Insira o nome de uma ou mais CTOs para obter os dados correspondentes.")

entrada_usuario = st.text_area("Digite os nomes das CTOs (uma por linha):")
botao_buscar = st.button("Buscar CTOs")

if entrada_usuario and botao_buscar:
    nomes_ctos = [cto.strip().upper() for cto in entrada_usuario.strip().split("\n") if cto.strip() != ""]

    resultados = []

    for nome in nomes_ctos:
        nome_final = nome

        # Se não encontrar diretamente na base, tenta corrigir via dicionário
        if nome not in df_base['cto'].str.upper().values:
            if nome in dict_corrigidos:
                nome_final = dict_corrigidos[nome]

        dados_cto = df_base[df_base['cto'].str.upper() == nome_final]

        if not dados_cto.empty:
            resultados.append(dados_cto)
        else:
            st.warning(f"⚠️ CTO '{nome}' não encontrada na base.")

    if resultados:
        df_resultado = pd.concat(resultados, ignore_index=True)
        st.success(f"✅ {len(df_resultado)} CTO(s) encontrada(s).")
        st.dataframe(df_resultado, use_container_width=True)

        # Download do resultado
        def gerar_excel():
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_resultado.to_excel(writer, index=False, sheet_name='Resultado')
            output.seek(0)
            return output

        st.download_button("📥 Baixar Resultado em Excel", gerar_excel(), file_name="resultado_busca_ctos.xlsx")
