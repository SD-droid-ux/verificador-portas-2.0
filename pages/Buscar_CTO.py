import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Buscar CTO", page_icon="🔍")

st.markdown("# 🔍 Buscar CTO")
st.write("Digite o nome de uma CTO para verificar seu nome corrigido (se aplicável).")

# Caminho do arquivo corrigido
caminho_corrigido = os.path.join("pages", "base_de_dados", "base_nomes_corrigidos.xlsx")

# Verifica se o arquivo existe
if not os.path.exists(caminho_corrigido):
    st.error("Arquivo com os nomes corrigidos não encontrado.")
    st.stop()

# Carrega o arquivo corrigido
df_corrigidos = pd.read_excel(caminho_corrigido)

# Garante que as colunas existam
if "cto_antigo" not in df_corrigidos.columns or "cto_novo" not in df_corrigidos.columns:
    st.error("A planilha deve conter as colunas 'cto_antigo' e 'cto_novo'.")
    st.stop()

# Converte para letras maiúsculas para evitar problemas de comparação
df_corrigidos["cto_antigo"] = df_corrigidos["cto_antigo"].astype(str).str.strip().str.upper()
df_corrigidos["cto_novo"] = df_corrigidos["cto_novo"].astype(str).str.strip().str.upper()

# Campo de entrada
entrada_usuario = st.text_input("Nome da CTO")

# Processa quando o usuário digitar algo
if entrada_usuario:
    entrada = entrada_usuario.strip().upper()

    # Verifica se encontrou a CTO na base corrigida
    linha_corrigida = df_corrigidos[df_corrigidos["cto_novo"] == entrada]

    if not linha_corrigida.empty:
        cto_antigo = linha_corrigida.iloc[0]["cto_antigo"]
        cto_novo = linha_corrigida.iloc[0]["cto_novo"]

        st.success("CTO encontrada na base corrigida!")
        st.write(f"🔄 Nome original: `{cto_antigo}`")
        st.write(f"✅ Nome corrigido: `{cto_novo}`")

        # Exibir possível troca
        df_resposta = pd.DataFrame({
            "Possível Troca": [f"{cto_antigo} → {cto_novo}"]
        })
        st.dataframe(df_resposta, use_container_width=True)

    else:
        st.warning("CTO não encontrada na base de nomes corrigidos.")
