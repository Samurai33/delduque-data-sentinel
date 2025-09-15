# Dashboard Streamlit - Tema Escuro

## 📊 Visão Geral

Este módulo contém um dashboard Streamlit moderno com tema escuro, desenvolvido para visualização interativa de dados. Inclui gráficos Plotly (donut, barras empilhadas, heatmap, mapa) com filtragem cruzada e layout responsivo.

## 🚀 Instalação

### Dependências Obrigatórias
```bash
pip install streamlit pandas plotly numpy
```

### Dependências Opcionais (Recomendadas)
```bash
# Para melhor captura de eventos nos gráficos Plotly
pip install streamlit-plotly-events
```

## 📋 Uso Básico

### Função Principal: `criar_dashboard(dataframe)`

```python
import pandas as pd
from delduquedatasentinel.app_dashboard import criar_dashboard

# Seu DataFrame deve conter estas colunas:
# - data: datas (pandas datetime ou strings parseáveis)
# - categoria: categorias/canais para o gráfico donut
# - regiao: siglas UF (ex: 'SP', 'RJ') para o mapa
# - valor: valores numéricos para agregações
# - dow: dia da semana (opcional, será derivado de 'data')
# - hora: hora do dia 0-23 (opcional, será derivado de 'data')

# Exemplo de DataFrame
df = pd.DataFrame({
    'data': pd.date_range('2024-01-01', periods=1000, freq='H'),
    'categoria': np.random.choice(['Vendas', 'Marketing', 'Suporte'], 1000),
    'regiao': np.random.choice(['SP', 'RJ', 'MG', 'RS'], 1000),
    'valor': np.random.exponential(100, 1000)
})

# Chamar o dashboard
criar_dashboard(df)
```

### Executar o Dashboard

1. **Salve seu código em um arquivo** (ex: `meu_dashboard.py`)
2. **Execute com Streamlit:**
   ```bash
   streamlit run meu_dashboard.py
   ```

## 🎨 Recursos Implementados

### ✅ Tema Escuro
- Fundo: `#1e1e2e` (evita fadiga visual)
- Texto: `#e0e0e0` (alta legibilidade)
- Cards com bordas sutis e gradientes

### ✅ Layout Responsivo
- **Sidebar colapsável** com todos os filtros
- **Cards organizados** em grid responsivo
- **Hierarquia visual** clara entre componentes

### ✅ Gráficos Interativos

#### 🍩 Donut Chart
- Participação percentual por categoria
- **Clique** para filtrar outros gráficos
- Animação de "pull" no setor selecionado

#### 📊 Barras Empilhadas/Agrupadas
- Evolução temporal por categoria
- Toggle entre modo empilhado e agrupado
- Eixos rotacionados para datas longas

#### 🔥 Heatmap
- Matriz dia-da-semana × hora
- **Seleção lasso/box** para filtrar períodos
- Escala de cores adaptada ao tema escuro

#### 🗺️ Mapa por UF
- Scatter geográfico com centroides aproximados
- Tamanho e cor baseados no valor agregado
- Fallback para gráfico de barras se UF inválida

### ✅ Tabela Estilizada
- Linhas alternadas com tons sutis
- Cabeçalho destacado
- Rolagem habilitada
- Formatação de valores monetários

### ✅ Filtragem Cruzada
- **Clique no donut** → filtra por categoria
- **Clique em barras** → filtra por data
- **Seleção lasso no heatmap** → filtra por período
- **Clique no mapa** → filtra por região
- **Botão "Reset filtros"** limpa todas as seleções

## 🔧 Configuração Avançada

### Personalizar Cores do Tema
```python
# Edite as constantes no início do arquivo app_dashboard.py
DARK_BG = "#1e1e2e"      # Fundo principal
DARK_TEXT = "#e0e0e0"    # Cor do texto
CARD_BG = "#262635"      # Fundo dos cards
CARD_BORDER = "rgba(255,255,255,0.06)"  # Borda dos cards
```

### Adicionar Novos Gráficos
```python
def meu_grafico_customizado(df: pd.DataFrame) -> go.Figure:
    # Seu código aqui
    fig = px.scatter(df, x="coluna1", y="coluna2")
    fig.update_layout(**PLOTLY_LAYOUT_DEFAULTS)  # Aplica tema escuro
    return fig
```

## 🗂️ Estrutura de Dados Esperada

| Coluna    | Tipo        | Descrição                              | Obrigatória |
|-----------|-------------|----------------------------------------|-------------|
| `data`    | datetime    | Datas/timestamps dos registros         | ✅ Sim      |
| `categoria` | string    | Categorias para segmentação            | ✅ Sim      |
| `regiao`  | string      | Siglas UF (SP, RJ, MG...) para mapa   | ✅ Sim      |
| `valor`   | numeric     | Valores numéricos para agregações     | ✅ Sim      |
| `dow`     | string/int  | Dia da semana (derivado se ausente)   | ❌ Não      |
| `hora`    | int         | Hora 0-23 (derivado se ausente)       | ❌ Não      |

## 🐛 Solução de Problemas

### Erro: "streamlit_plotly_events not found"
- **Solução:** É opcional. O dashboard funciona sem esse pacote, mas com menor interatividade.
- **Instalar:** `pip install streamlit-plotly-events`

### Mapa não exibe UFs corretamente
- **Causa:** Coluna `regiao` não contém siglas UF válidas
- **Solução:** Use siglas como 'SP', 'RJ', 'MG', etc., ou forneça colunas `lat`/`lon`

### Performance lenta com muitos dados
- **Soluções:**
  - Filtre dados antes de chamar `criar_dashboard()`
  - Use amostragem: `df.sample(n=5000)`
  - Agrupe dados por período antes da visualização

## 📝 Exemplo Completo

```python
# exemplo_dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
from delduquedatasentinel.app_dashboard import criar_dashboard

st.set_page_config(page_title="Meu Dashboard", layout="wide")

# Dados sintéticos para teste
@st.cache_data
def gerar_dados_teste():
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=2000, freq='H')
    
    return pd.DataFrame({
        'data': np.random.choice(dates, 1500),
        'categoria': np.random.choice(['Vendas', 'Marketing', 'Suporte', 'Financeiro'], 1500),
        'regiao': np.random.choice(['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA'], 1500),
        'valor': np.random.exponential(150, 1500).round(2)
    })

# Upload de arquivo ou dados sintéticos
uploaded = st.file_uploader("Upload CSV (opcional)", type=['csv'])
if uploaded:
    df = pd.read_csv(uploaded)
else:
    df = gerar_dados_teste()

# Renderizar dashboard
criar_dashboard(df)
```

## 📄 Licença

Este projeto segue a mesma licença do projeto principal Delduque Data Sentinel.