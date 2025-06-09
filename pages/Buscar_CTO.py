import os
import pandas as pd
import streamlit as st

# Caminhos dos arquivos
caminho_corrigido = os.path.join("pages", "base_de_dados", "base_nomes_corrigidos.xlsx")
caminho_base_rede = os.path.join("pages", "base_de_dados", "base.xlsx")

# Título da aba
st.title("🔍 Buscar CTO")

# Entrada de texto para múltiplas CTOs
input_ctos = st.text_area("Digite o(s) nome(s) da(s) CTO(s):", placeholder="Ex: FLA1234\nFLA5678")

# Botão de busca
if st.button("🔎 Buscar"):
    if not input_ctos.strip():
        st.warning("Por favor, insira ao menos um nome de CTO.")
    else:
        # Processa entradas
        lista_ctos = [cto.strip().upper() for cto in input_ctos.replace(",", "\n").splitlines() if cto.strip()]

        # Carrega os dados
        df_corrigidos = pd.read_excel(caminho_corrigido)
        df_base = pd.read_excel(caminho_base_rede)

        # Normaliza colunas
        df_corrigidos["cto_antigo"] = df_corrigidos["cto_antigo"].astype(str).str.strip().str.upper()
        df_corrigidos["cto_novo"] = df_corrigidos["cto_novo"].astype(str).str.strip().str.upper()
        df_base["cto"] = df_base["cto"].astype(str).str.strip().str.upper()

        resultados = []

        for entrada in lista_ctos:
            # Tenta encontrar nome novo com base na correção
            linha_corrigida = df_corrigidos[
                (df_corrigidos["cto_antigo"] == entrada) | (df_corrigidos["cto_novo"] == entrada)
            ]

            if not linha_corrigida.empty:
                nome_corrigido = linha_corrigida.iloc[0]["cto_novo"]
            else:
                nome_corrigido = entrada

            # Busca na base principal
            linha_base = df_base[df_base["cto"] == nome_corrigido]

            if not linha_base.empty:
                resultados.append(linha_base)
            else:
                st.warning(f"❌ CTO '{entrada}' não encontrada na base.")

        # Exibe resultados
        if resultados:
            df_resultado = pd.concat(resultados, ignore_index=True)
            st.success(f"✅ {len(df_resultado)} CTO(s) encontrada(s):")
            st.dataframe(df_resultado)

            # Download CSV
            csv = df_resultado.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Baixar resultado em CSV", data=csv, file_name="resultado_busca_cto.csv", mime="text/csv")
        else:
            st.info("Nenhuma CTO válida foi encontrada.")
