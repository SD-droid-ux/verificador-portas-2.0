import streamlit as st
import pandas as pd
import os
from rapidfuzz import fuzz, process

st.title("🔍 Buscar por CTO")

# Caminhos das bases
caminho_base = os.path.join("pages", "base_de_dados", "base.xlsx")
caminho_correcao = os.path.join("pages", "base_de_dados", "base_nomes_corrigidos.xlsx")

# Carrega as bases
try:
    df_base = pd.read_excel(caminho_base)
    df_corrigidos = pd.read_excel(caminho_correcao)
except FileNotFoundError:
    st.error("❌ Base principal ou base de nomes corrigidos não encontrada.")
    st.stop()

# Adiciona coluna CAMINHO_REDE
df_base["CAMINHO_REDE"] = df_base["pop"].astype(str) + "/" + df_base["olt"].astype(str) + "/" + df_base["slot"].astype(str) + "/" + df_base["pon"].astype(str)

# Estados únicos
estados = sorted(df_base["estado"].dropna().unique())
estado_selecionado = st.selectbox("📍 Selecione o Estado", ["Todos"] + estados)

# Aplica filtro por estado
if estado_selecionado != "Todos":
    df_filtrado = df_base[df_base["estado"] == estado_selecionado]
else:
    df_filtrado = df_base.copy()

# Lista de POPs
pops_unicos = sorted(df_filtrado["pop"].dropna().unique())
pop_selecionado = st.selectbox("📡 Selecione o POP", ["Todos"] + pops_unicos)

if pop_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["pop"] == pop_selecionado]

# Entrada do usuário
input_ctos = list(dict.fromkeys(st.text_area("✍️ Insira os nomes das CTOs (uma por linha)", height=150).upper().splitlines()))

# Processamento ao clicar no botão
if st.button("🔍 Buscar CTOs"):
    if not input_ctos or all(not cto.strip() for cto in input_ctos):
        st.warning("⚠️ Insira pelo menos um nome de CTO.")
    else:
        st.info("🔎 Buscando CTOs...")

        resultados = []

        for entrada in input_ctos:
            entrada = entrada.strip()

            # Verifica correspondência direta na base principal
            encontrados_direto = df_filtrado[df_filtrado["cto"].str.upper() == entrada]

            if not encontrados_direto.empty:
                encontrados_direto["ORIGEM"] = "🟢 Encontrado diretamente"
                resultados.append(encontrados_direto)
                continue

            # Verifica na base de nomes corrigidos
            linha_corrigida = df_corrigidos[
                (df_corrigidos["cto_novo"].str.upper() == entrada)
                | (df_corrigidos["cto_antigo"].str.upper() == entrada)
            ]

            if not linha_corrigida.empty:
                nome_antigo = linha_corrigida.iloc[0]["nome_antigo"].strip().upper()
                encontrados_indireto = df_filtrado[df_filtrado["cto"].str.upper() == nome_antigo]
                if not encontrados_indireto.empty:
                    encontrados_indireto["ORIGEM"] = "🟡 Encontrado via correspondência nome corrigido"
                    resultados.append(encontrados_indireto)
                    continue

            # Tenta correspondência por similaridade (opcional)
            todas_ctos = df_filtrado["cto"].astype(str).str.upper().tolist()
            correspondencia, score, _ = process.extractOne(entrada, todas_ctos, scorer=fuzz.ratio)
            if score >= 85:
                similares = df_filtrado[df_filtrado["cto"].str.upper() == correspondencia].copy()
                similares["ORIGEM"] = f"🟠 Similar a '{correspondencia}' ({score}%)"
                resultados.append(similares)
            else:
                resultados.append(pd.DataFrame([{
                    "cto": entrada,
                    "ORIGEM": "🔴 Não encontrada"
                }]))

        # Junta e exibe
        df_resultado = pd.concat(resultados, ignore_index=True)

        if "CAMINHO_REDE" in df_resultado.columns:
            portas_por_caminho = df_base.groupby("CAMINHO_REDE")["portas"].sum().to_dict()

            def obter_status(row):
                total = portas_por_caminho.get(row["CAMINHO_REDE"], 0)
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

            df_resultado["STATUS"] = df_resultado.apply(obter_status, axis=1)

        # Filtro por POP final após exibição
        pops_resultado = sorted(df_resultado["pop"].dropna().unique())
        pop_final = st.selectbox("🔎 Filtrar resultados por POP (opcional)", ["Todos"] + pops_resultado)
        if pop_final != "Todos":
            df_resultado = df_resultado[df_resultado["pop"] == pop_final]

        st.success(f"✅ {len(df_resultado)} CTO(s) encontradas.")
        st.dataframe(df_resultado)
