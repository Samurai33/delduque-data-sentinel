"""
exemplo_dashboard.py

Arquivo de exemplo para testar o dashboard com tema escuro.
Execute: streamlit run exemplo_dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

# Adicionar o diretório atual ao path para importar app_dashboard
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app_dashboard import criar_dashboard

# Configuração da página
st.set_page_config(
    page_title="Dashboard Tema Escuro - Demo", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌙 Demo: Dashboard com Tema Escuro")
st.markdown("**Desenvolvido para o projeto Delduque Data Sentinel**")

# Gerar dados sintéticos para demonstração
@st.cache_data
def gerar_dados_demonstracao():
    """Gera dados sintéticos para demonstrar o dashboard."""
    np.random.seed(42)  # Para resultados reproduzíveis
    
    # Datas dos últimos 60 dias com registros a cada hora
    end_date = pd.Timestamp.now()
    start_date = end_date - pd.Timedelta(days=60)
    date_range = pd.date_range(start=start_date, end=end_date, freq='h')
    
    # Gerar 2000 registros aleatórios
    n_records = 2000
    
    df = pd.DataFrame({
        'data': np.random.choice(date_range, n_records),
        'categoria': np.random.choice([
            'Vendas Online', 'Marketing Digital', 'Suporte Técnico', 
            'Financeiro', 'Recursos Humanos', 'Operações'
        ], n_records),
        'regiao': np.random.choice([
            'SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'GO', 
            'PE', 'CE', 'PA', 'DF', 'ES', 'PB', 'RN', 'MT'
        ], n_records),
        'valor': np.random.exponential(scale=200, size=n_records).round(2)
    })
    
    # Adicionar algumas tendências realistas
    # Vendas maiores durante horário comercial
    df.loc[
        (df['categoria'] == 'Vendas Online') & 
        (df['data'].dt.hour.between(9, 18)), 
        'valor'
    ] *= 1.5
    
    # Suporte técnico mais ativo à tarde
    df.loc[
        (df['categoria'] == 'Suporte Técnico') & 
        (df['data'].dt.hour.between(14, 20)), 
        'valor'
    ] *= 1.3
    
    return df.sort_values('data').reset_index(drop=True)

# Interface para upload ou dados sintéticos
st.sidebar.header("📁 Fonte de Dados")
opcao_dados = st.sidebar.radio(
    "Escolha a fonte:",
    ["Dados de demonstração", "Upload de arquivo CSV"]
)

if opcao_dados == "Upload de arquivo CSV":
    uploaded_file = st.sidebar.file_uploader(
        "Selecione um arquivo CSV",
        type=['csv'],
        help="O arquivo deve conter as colunas: data, categoria, regiao, valor"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.sidebar.success(f"✅ Arquivo carregado: {len(df)} registros")
        except Exception as e:
            st.sidebar.error(f"❌ Erro ao carregar arquivo: {e}")
            df = gerar_dados_demonstracao()
    else:
        st.sidebar.info("Aguardando upload do arquivo...")
        df = gerar_dados_demonstracao()
else:
    df = gerar_dados_demonstracao()
    st.sidebar.info(f"📊 Usando dados sintéticos: {len(df)} registros")

# Informações sobre os dados
st.sidebar.markdown("---")
st.sidebar.markdown("**💡 Dica:**")
st.sidebar.markdown(
    "• Clique nos gráficos para filtrar\n"
    "• Use a seleção lasso no heatmap\n" 
    "• Botão 'Reset filtros' limpa tudo"
)

# Mostrar amostra dos dados (opcional)
if st.sidebar.checkbox("🔍 Mostrar amostra dos dados"):
    st.subheader("📋 Amostra dos Dados")
    st.dataframe(df.head(10), use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Registros", f"{len(df):,}")
    with col2:
        st.metric("Categorias Únicas", df['categoria'].nunique())
    with col3:
        st.metric("Regiões (UF)", df['regiao'].nunique())
    
    st.markdown("---")

# Renderizar o dashboard principal
try:
    criar_dashboard(df)
except Exception as e:
    st.error(f"❌ Erro ao renderizar o dashboard: {e}")
    st.info("Verifique se as colunas necessárias estão presentes: data, categoria, regiao, valor")

# Footer com informações
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        🚀 Dashboard criado com Streamlit e Plotly | 
        📚 <a href='README_DASHBOARD.md' style='color: #25c5c0;'>Documentação completa</a> | 
        🎨 Tema escuro para reduzir fadiga visual
    </div>
    """,
    unsafe_allow_html=True
)