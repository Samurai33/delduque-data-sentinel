
# Desduque Data Sentinel

# Instruções para executar o Desduque Data Sentinel

O Desduque Data Sentinel foi desenvolvido em **Streamlit** e utiliza **pandas** e **plotly** para manipulação e visualização de dados.

## Pré-requisitos

- Python 3.8 ou superior instalado.
- Pacotes listados em `requirements.txt`.

## Passos para rodar localmente

1. **Criar ambiente virtual (opcional, mas recomendado)**

   ```bash
   python -m venv .venv
   # No macOS/Linux:
   source .venv/bin/activate
   # No Windows:
   .venv\Scripts\activate
   ```

2. **Instalar as dependências**

   ```bash
   pip install -r requirements.txt
   ```

3. **Executar o Streamlit**

   ```bash
   streamlit run app.py
   ```

4. **Abrir no navegador**

   O terminal exibirá um URL (por padrão `http://localhost:8501`). Copie e cole no navegador para acessar o painel.

## Sobre o Desduque Data Sentinel

- O aplicativo lê todas as abas da planilha `BASE DESDUQUE DATA SENTINEL.xlsx`, mas foca nas abas **ATIVOS PF E PJ** e **CANCELADOS**.
- Filtros interativos permitem selecionar **Usuário responsável**, **Categoria**, **Estado** e um intervalo de datas.
- Métricas-chave (KPIs) exibem o total de registros filtrados, quantidade de categorias distintas e novos registros nos últimos 30 dias.
- Gráficos interativos mostram:
  - Top 10 responsáveis (gráfico de barras)
  - Evolução temporal de registros (linha)
  - Distribuição por categoria (barras)
- A área de prévia de dados exibe os registros filtrados em forma de tabela.

O design segue boas práticas de visualização de dados, priorizando clareza, hierarquia visual e escolha adequada de gráficos.
