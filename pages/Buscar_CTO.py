import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Buscar CTO", page_icon="🔍")
st.markdown("# 🔍 Buscar CTO")
st.write("Digite o nome de uma CTO para verificar o nome corrigido e os dados da rede.")

# Caminhos dos arquivos
caminho_corrigido = os.path.join("data", "base_ctos_corrigidas.xlsx")
caminho_base_rede = os.path.join("data", "base.xlsx")

# Verificações
if not os.path.exists(caminho_corrigido):
    st.error("Arquivo com os nomes corrigidos não encontrado.")
    st.stop()

if not os.path.exists(caminho_base_rede):
    st.error("Arquivo com a base de rede não encontrado.")
    st.stop()

# Carregar bases
df_corrigidos = pd.read_excel(caminho_corrigido)
df_rede = pd.read_excel(caminho_base_rede)

# Padronização
df_corrigidos["cto_antigo"] = df_corrigidos["cto_antigo"].astype(str).str.strip().str.upper()
df_corrigidos["cto_novo"] = df_corrigidos["cto_novo"].astype(str).str.strip().str.upper()
df_rede["cto"] = df_rede["cto"].astype(str).str.strip().str.upper()

# Entrada do usuário
entrada_usuario = st.text_input("Nome da CTO")
botao_buscar = st.button("🔍 Buscar")

if botao_buscar and entrada_usuario:
    entrada = entrada_usuario.strip().upper()
    linha_corrigida = df_corrigidos[df_corrigidos["cto_novo"] == entrada]

    if not linha_corrigida.empty:
        cto_antigo = linha_corrigida.iloc[0]["cto_antigo"]
        cto_novo = linha_corrigida.iloc[0]["cto_novo"]

        st.success("CTO encontrada na base corrigida!")
        st.write(f"🔄 Nome original: `{cto_antigo}`")
        st.write(f"✅ Nome corrigido: `{cto_novo}`")

        # Dados da rede
        dados_rede = df_rede[df_rede["cto"] == cto_novo]

        if not dados_rede.empty:
            st.subheader("📡 Detalhes do Caminho de Rede:")
            st.dataframe(dados_rede, use_container_width=True)
        else:
            st.warning("CTO corrigida encontrada, mas não foi localizada na base de rede.")
    else:
        st.warning("CTO não encontrada na base de nomes corrigidos.")
