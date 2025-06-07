import streamlit as st
import time
import pandas as pd
import os
from rapidfuzz import process, fuzz

st.title("🔍 Buscar por CTO")

# Caminho da base de dados
caminho_base = os.path.join("pages", "base_de_dados", "base.xlsx")

# Carrega os dados na sessão
if "df" not in st.session_state or "portas_por_caminho" not in st.session_state:
    try:
        df = pd.read_excel(caminho_base)
        df["CAMINHO_REDE"] = df["pop"].astype(str) + "/" + df["olt"].astype(str) + "/" + df["slot"].astype(str) + "/" + df["pon"].astype(str)
        portas_por_caminho = df.groupby("CAMINHO_REDE")["portas"].sum().to_dict()
        st.session_state["df"] = df
        st.session_state["portas_por_caminho"] = portas_por_caminho
    except FileNotFoundError:
        st.warning("⚠️ A base de dados não foi encontrada. Por favor, envie na página principal.")
        st.stop()

# Função de normalização
def normalizar(texto):
    return str(texto).upper().strip().replace("-", "").replace("_", "").replace(" ", "")

# Dados da sessão
df = st.session_state["df"]
portas_por_caminho = st.session_state["portas_por_caminho"]

# Filtro por estado
estados_disponiveis = df["estado"].dropna().unique()
estado_selecionado = st.selectbox("🗺️ Selecione o estado:", sorted(estados_disponiveis))

df_estado = df[df["estado"] == estado_selecionado].copy()

# Se for RN ou CE, exige filtro adicional por POP
pop_filtrado = None
if estado_selecionado in ["RN", "CE"]:
    pops_disponiveis = df_estado["pop"].dropna().unique()
    pop_filtrado = st.selectbox("🏢 Selecione o POP:", sorted(pops_disponiveis))
    df_estado = df_estado[df_estado["pop"] == pop_filtrado]

# Pré-processamento
df_estado["cto_norm"] = df_estado["cto"].apply(normalizar)

# Entrada das CTOs
input_ctos = list(dict.fromkeys(st.text_area("✏️ Insira os ID das CTOs (uma por linha)").splitlines()))

if st.button("🔍 Buscar CTOs"):
    if not input_ctos or all(not cto.strip() for cto in input_ctos):
        st.warning("⚠️ Insira pelo menos um ID de CTO para buscar.")
    else:
        with st.spinner("🔄 Analisando CTOs..."):
            progress_bar = st.progress(0)
            for i in range(5):
                time.sleep(0.1)
                progress_bar.progress((i + 1) * 20)

            resultados_finais = []

            for cto_input in input_ctos:
                cto_input_norm = normalizar(cto_input)

                melhores = process.extract(
                    cto_input_norm,
                    df_estado["cto_norm"].unique(),
                    scorer=fuzz.WRatio,
                    limit=1
                )

                if melhores and melhores[0][1] > 65:
                    cto_norm_encontrado = melhores[0][0]
                    match_df = df_estado[df_estado["cto_norm"] == cto_norm_encontrado].copy()
                    match_df["cto_busca"] = cto_input
                    match_df["cto_sugerido"] = match_df["cto"]
                    match_df["score_correspondencia"] = melhores[0][1]
                    resultados_finais.append(match_df)
                else:
                    linha_nao_encontrada = pd.DataFrame([{
                        "cto_busca": cto_input,
                        "cto_sugerido": "❌ Nenhuma correspondência aceitável",
                        "score_correspondencia": 0,
                    }])
                    resultados_finais.append(linha_nao_encontrada)

            if resultados_finais:
                df_resultado = pd.concat(resultados_finais, ignore_index=True)
                df_resultado = df_resultado.sort_values(by="score_correspondencia", ascending=False)

                if "CAMINHO_REDE" in df_resultado.columns and "portas" in df_resultado.columns:
                    def obter_status(row):
                        total = portas_por_caminho.get(row.get("CAMINHO_REDE", ""), 0)
                        if total > 128:
                            return "🔴 SATURADO"
                        elif total == 128 and row["portas"] == 16:
                            return "🔴 SATURADO"
                        elif total == 128 and row["portas"] == 8:
                            return "🔴 CTO É SP8 MAS PON JÁ ESTÁ SATURADA"
                        elif row["portas"] == 16 and total < 128:
                            return "✅ CTO JÁ É SP16 MAS A PON NÃO ESTÁ SATURADA"
                        elif row["portas"] == 8 and total < 128:
                            return "✅ TROCA DE SP8 PARA SP16"
                        else:
                            return "⚪ STATUS INDEFINIDO"

                    df_resultado["STATUS"] = df_resultado.apply(
                        lambda row: obter_status(row) if "portas" in row and pd.notna(row.get("CAMINHO_REDE", None)) else "N/A",
                        axis=1
                    )

                st.success(f"✅ {len(df_resultado)} resultado(s) encontrados com correspondência.")

                # Filtro por POP após resultado (para SP, MG etc.)
                if estado_selecionado not in ["RN", "CE"]:
                    pops_result = df_resultado["pop"].dropna().unique()
                    pop_pos_busca = st.selectbox("📍 Filtrar por POP (opcional):", options=["Todos"] + sorted(pops_result.tolist()))
                    if pop_pos_busca != "Todos":
                        df_resultado = df_resultado[df_resultado["pop"] == pop_pos_busca]

                st.dataframe(df_resultado)

            else:
                st.info("🔍 Nenhuma CTO encontrada com correspondência aceitável.")

        progress_bar.empty()
