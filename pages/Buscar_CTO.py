import os
import pandas as pd
import streamlit as st

# Caminhos dos arquivos
caminho_corrigido = os.path.join("pages", "base_de_dados", "base_nomes_corrigidos.xlsx")
caminho_base_rede = os.path.join("pages", "base_de_dados", "base.xlsx")

# Título da aba
st.title("🔍 Buscar CTO")

# Entrada do usuário
input_ctos = st.text_area("Digite o(s) nome(s) da(s) CTO(s):", placeholder="Ex: FLA1234\nFLA5678")

# Botão para iniciar a busca
if st.button("🔎 Buscar"):
    if not input_ctos.strip():
        st.warning("Por favor, insira ao menos um nome de CTO.")
    else:
        # Lista de CTOs normalizadas
        lista_ctos = [cto.strip().upper() for cto in input_ctos.replace(",", "\n").splitlines() if cto.strip()]

        # Carregar os dados
        df_corrigidos = pd.read_excel(caminho_corrigido)
        df_base = pd.read_excel(caminho_base_rede)

        # Normalizar colunas
        df_corrigidos["cto_antigo"] = df_corrigidos["cto_antigo"].astype(str).str.strip().str.upper()
        df_corrigidos["cto_novo"] = df_corrigidos["cto_novo"].astype(str).str.strip().str.upper()
        df_base["cto"] = df_base["cto"].astype(str).str.strip().str.upper()

        resultados = []

        for entrada in lista_ctos:
            # 1. Tenta buscar diretamente na base
            linha_base = df_base[df_base["cto"] == entrada]

            # 2. Se não encontrar, tenta usar a base de nomes corrigidos
            if linha_base.empty:
                match_corrigido = df_corrigidos[df_corrigidos["cto_novo"] == entrada]
                if not match_corrigido.empty:
                    nome_antigo = match_corrigido.iloc[0]["cto_antigo"]
                    linha_base = df_base[df_base["cto"] == nome_antigo]

            # 3. Salva o resultado (se encontrado)
            if not linha_base.empty:
                resultados.append(linha_base)
            else:
                st.warning(f"❌ CTO '{entrada}' não encontrada na base.")

        # Exibir resultado final
        if resultados:
            df_resultado = pd.concat(resultados, ignore_index=True)
            st.success(f"✅ {len(df_resultado)} CTO(s) encontrada(s):")
            st.dataframe(df_resultado)

            # Download CSV
            csv = df_resultado.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Baixar resultado em CSV", data=csv, file_name="resultado_busca_cto.csv", mime="text/csv")
        else:
            st.info("Nenhuma CTO válida foi encontrada.")
