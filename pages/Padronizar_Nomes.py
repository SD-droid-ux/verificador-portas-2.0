import streamlit as st
import pandas as pd
import os

st.title("🔄 Ver Nome Antigo e Novo da CTO")

# Caminho fixo para a base
caminho_base = os.path.join("pages", "base_de_dados", "base_nomes_corrigidos.xlsx")

# Tenta carregar a base
try:
    df_base = pd.read_excel(caminho_base)

    # Padroniza colunas
    df_base["cto_antigo"] = df_base["cto_antigo"].astype(str).str.strip().str.upper()
    df_base["cto_novo"] = df_base["cto_novo"].astype(str).str.strip().str.upper()

    # Entrada manual das CTOs
    entrada = st.text_area("✍️ Insira os nomes das CTOs (uma por linha):", height=200)
    lista_ctos = [cto.strip().upper() for cto in entrada.split('\n') if cto.strip()]

    if lista_ctos:
        resultados = []

        for cto in lista_ctos:
            filtro = df_base[(df_base["cto_antigo"] == cto) | (df_base["cto_novo"] == cto)]
            if not filtro.empty:
                for _, linha in filtro.iterrows():
                    resultados.append({
                        "CTO digitada": cto,
                        "Nome Antigo": linha["cto_antigo"],
                        "Nome Novo": linha["cto_novo"]
                    })
            else:
                resultados.append({
                    "CTO digitada": cto,
                    "Nome Antigo": "❌ Não encontrado",
                    "Nome Novo": "❌ Não encontrado"
                })

        df_resultado = pd.DataFrame(resultados)
        st.success(f"🔍 Foram encontradas {len(df_resultado)} correspondência(s).")
        st.dataframe(df_resultado)

    else:
        st.info("⚠️ Digite ao menos uma CTO para buscar.")

except FileNotFoundError:
    st.error("❌ A base 'base_nomes_corrigidos.xlsx' não foi encontrada no caminho esperado.")
