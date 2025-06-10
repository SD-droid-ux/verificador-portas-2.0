import pandas as pd

# Leitura do Excel
df = pd.read_excel("entrada.xlsx")

# Renomear colunas para padronizar
df.columns = ['pop', 'olt', 'slot', 'pon', 'cto']

# Remover espaços extras e padronizar
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# Extrair número da CTO
df['numero_cto'] = df['cto'].str.extract(r'(\d+)$')

# Determinar número de portas com base na regra (se número <= 128 → 8 portas, senão → 16 portas)
df['portas'] = df['numero_cto'].astype(int).apply(lambda x: 8 if x <= 128 else 16)

# Calcular o total de CTOs por agrupamento
agrupado = df.groupby(['pop', 'olt', 'slot', 'pon']).agg(
    total=('cto', 'count')
).reset_index()

# Juntar os totais com o dataframe original
df_final = pd.merge(df, agrupado, on=['pop', 'olt', 'slot', 'pon'])

# Selecionar e reordenar colunas para exportação
df_final = df_final[['pop', 'olt', 'slot', 'pon', 'cto', 'portas', 'total']]

# Exportar para Excel
df_final.to_excel("saida_formatada.xlsx", index=False)
