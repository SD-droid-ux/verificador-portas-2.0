import pandas as pd
import os

# Caminho para a base original
caminho_base = os.path.join("pages", "base_de_dados", "base.xlsx")

# Função principal
def verificar_saturacao_portas(df_novas):
    # 1. Agrupar portas novas por caminho de rede
    df_novas['caminho_rede'] = df_novas[['pop', 'olt', 'slot', 'pon']].agg('/'.join, axis=1)
    portas_novas = df_novas.groupby('caminho_rede')['portas'].sum().reset_index()
    portas_novas.rename(columns={'portas': 'portas_novas'}, inplace=True)

    # 2. Carregar a base existente
    df_base = pd.read_excel(caminho_base)
    df_base['caminho_rede'] = df_base[['pop', 'olt', 'slot', 'pon']].agg('/'.join, axis=1)
    portas_existentes = df_base.groupby('caminho_rede')['portas'].sum().reset_index()
    portas_existentes.rename(columns={'portas': 'portas_existentes'}, inplace=True)

    # 3. Juntar bases
    df_total = pd.merge(portas_existentes, portas_novas, on='caminho_rede', how='outer').fillna(0)
    df_total['portas_existentes'] = df_total['portas_existentes'].astype(int)
    df_total['portas_novas'] = df_total['portas_novas'].astype(int)

    # 4. Calcular total final
    df_total['total_final'] = df_total['portas_existentes'] + df_total['portas_novas']
    df_total['status'] = df_total['total_final'].apply(lambda x: 'ULTRAPASSOU' if x > 128 else 'OK')

    # Reorganizar colunas
    return df_total[['caminho_rede', 'portas_existentes', 'portas_novas', 'total_final', 'status']]
