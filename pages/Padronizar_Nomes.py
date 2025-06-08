import streamlit as st
import pandas as pd
import os

st.title("🔁 Buscar Nome Novo ou Antigo da CTO")

# Caminho fixo do arquivo
caminho_base = os.path.join("pages", "base_nomes_corrigidos.xlsx")

try:
    # Carrega a base corrigida
    df_base = pd.read_excel(caminho_base)
    df_base["cto_antigo"] = df_base["cto_antigo"].astype(str).str.strip().str.upper()
    df_base["cto_novo"] = df_base["cto_novo"].astype(str).str.strip().str.upper()

    # Entrada de várias CTOs
    entrada = st.text_area("📥 Insira uma ou mais CTOs (uma por linha):")

    if entrada:
        ctos_input = [cto.strip().upper() for cto in entrada.strip().split("\n") if cto.strip()]
        resultados = []

        for cto in ctos_input:
            if cto in df_base["cto_antigo"].values:
                linha = df_base[df_base["cto_antigo"] == cto].iloc[0]
                resultados.append({
                    "CTO Informada": cto,
                    "Nome Antigo": linha["cto_antigo"],
                    "Nome Novo": linha["cto_novo"]
                })
            elif cto in df_base["cto_novo"].values:
                linha = df_base[df_base["cto_novo"] == cto].iloc[0]
                resultados.append({
                    "CTO Informada": cto,
                    "Nome Antigo": linha["cto_antigo"],
                    "Nome Novo": linha["cto_novo"]
                })
            else:
                resultados.append({
                    "CTO Informada": cto,
                    "Nome Antigo": "❌ Não encontrado",
                    "Nome Novo": "❌ Não encontrado"
                })

        df_resultado = pd.DataFrame(resultados)
        st.success("✅ Resultado da busca:")
        st.dataframe(df_resultado, use_container_width=True)

except FileNotFoundError:
    st.error("❌ Arquivo 'base_nomes_corrigidos.xlsx' não encontrado no diretório 'pages'.")
except Exception as e:
    st.error(f"❌ Erro ao carregar ou processar a base: {e}")
