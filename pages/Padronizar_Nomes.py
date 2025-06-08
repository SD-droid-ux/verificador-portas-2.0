import streamlit as st
import pandas as pd
import io

st.title("🔁 Conversor Inteligente de Nomes de CTOs")

# Upload da base
uploaded_file = st.file_uploader("📤 Faça upload da base base_nomes_corrigidos.xlsx", type=["xlsx"])

if uploaded_file:
    try:
        # Lê a base
        df_base = pd.read_excel(uploaded_file)
        df_base["cto_antigo"] = df_base["cto_antigo"].astype(str).str.strip().str.upper()
        df_base["cto_novo"] = df_base["cto_novo"].astype(str).str.strip().str.upper()

        # Entrada de múltiplas CTOs
        entrada_ctos = st.text_area("✍️ Insira uma ou mais CTOs (nome antigo ou novo), uma por linha:")
        
        if entrada_ctos:
            ctos_input = [cto.strip().upper() for cto in entrada_ctos.strip().split("\n") if cto.strip()]
            resultados = []

            for cto in ctos_input:
                linha = df_base[df_base["cto_antigo"] == cto]
                if not linha.empty:
                    resultados.append({"CTO Informada": cto, "Nome Antigo": cto, "Nome Novo": linha["cto_novo"].values[0]})
                else:
                    linha = df_base[df_base["cto_novo"] == cto]
                    if not linha.empty:
                        resultados.append({"CTO Informada": cto, "Nome Antigo": linha["cto_antigo"].values[0], "Nome Novo": cto})
                    else:
                        resultados.append({"CTO Informada": cto, "Nome Antigo": "❌ Não encontrado", "Nome Novo": "❌ Não encontrado"})

            df_resultado = pd.DataFrame(resultados)
            st.success("✅ Resultado encontrado:")
            st.dataframe(df_resultado)

            # Botão para download em Excel
            def converter_para_excel(df):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Resultado')
                return output.getvalue()

            st.download_button(
                label="📥 Baixar resultado em Excel",
                data=converter_para_excel(df_resultado),
                file_name="resultado_ctos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"Erro ao processar a planilha: {e}")
