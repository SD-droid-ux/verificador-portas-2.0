# 📊 Verificador de Portas por Caminho de Rede

Este aplicativo em Streamlit permite verificar a saturação de portas por caminho de rede, baseado em uma planilha Excel com dados de CTOs.

## 🚀 Como usar

1. Faça o upload de uma planilha `.xlsx` com as colunas:
   - POP, CHASSI, PLACA, OLT, PORTAS, ID CTO, CIDADE, NOME ANTIGO CTO
2. Use a aba lateral para:
   - Ver a visão geral (CTOs, total de portas, caminhos saturados)
   - Buscar por CTO e verificar status

## ▶️ Execute localmente

```bash
pip install -r requirements.txt
streamlit run main.py
