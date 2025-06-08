import streamlit as st
import pandas as pd
import os

st.title("🔁 Conversor de CTO Antiga para Nova")

# Caminho do arquivo
caminho_base = os.path.join("pages", "base_de_dados", "base_nomes_corrigidos.xlsx")

# Carrega a base de dados
try:
    df = pd.read_excel(caminho_base)
    df['cto_antigo'] = df['cto_antigo'].astype(str).str.strip().str.upper()
    df['cto_novo'] = df['cto_novo'].astype(str).str.strip().str.upper()
except Exception as e:
    st.error(f"Erro ao carregar a base: {e}")
    st.stop()

# Entrada do usuário
cto_input = st.text_input("Digite o nome antigo da CTO:")

if cto_input:
    cto_input = cto_input.strip().upper()
    resultado = df[df['cto_antigo'] == cto_input]

    if not resultado.empty:
        nome_novo = resultado['cto_novo'].values[0]
        st.success(f"✅ Nome novo correspondente: `{nome_novo}`")
    else:
        st.warning("❌ CTO não encontrada na base de dados.")
