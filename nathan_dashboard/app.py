import os
def print_ascii_art():
    asciiart_path = os.path.join(os.path.dirname(__file__), '..', 'asciiart')
    try:
        with open(asciiart_path, 'r', encoding='utf-8') as f:
            art = f.read()
        print(art)
    except Exception as e:
        print('Não foi possível carregar a arte ASCII:', e)

print_ascii_art()
import streamlit as st
import pandas as pd
import plotly.express as px


@st.cache_data(show_spinner=False)
def load_data(file_path: str):
    """
    Carrega todas as abas de um arquivo Excel em um dicionário de DataFrames.

    O uso de `st.cache_data` garante que o arquivo só seja lido uma vez durante
    a sessão, melhorando a performance.
    """
    xls = pd.ExcelFile(file_path)
    data = {}
    for name in xls.sheet_names:
        try:
            df = xls.parse(name)
            data[name] = df
        except Exception:
            # ignore sheets that cannot be parsed
            pass
    return data


def prepare_dataframe(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """
    Formata a coluna de data para o tipo datetime e remove registros sem data.

    Args:
        df: DataFrame original
        date_col: nome da coluna de data
    Returns:
        DataFrame com a coluna de data convertida
    """
    df = df.copy()
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
    return df


def filter_dataframe(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """
    Cria filtros interativos e retorna o DataFrame filtrado.

    Os filtros são exibidos na barra lateral do Streamlit (sidebar) e incluem:
      - Usuário responsável
      - Categoria
      - Estado
      - Período de datas

    Args:
        df: DataFrame original
        date_col: nome da coluna de data
    Returns:
        DataFrame filtrado conforme os filtros selecionados
    """
    # Filtros de usuário responsável
    responsible_values = sorted(df['Usuário responsável'].dropna().unique()) if 'Usuário responsável' in df.columns else []
    selected_responsibles = st.sidebar.multiselect(
        'Usuário responsável', responsible_values, default=[]
    )

    # Filtros de categoria
    category_values = sorted(df['Categoria'].dropna().unique()) if 'Categoria' in df.columns else []
    selected_categories = st.sidebar.multiselect(
        'Categoria', category_values, default=[]
    )

    # Filtro de estado
    state_values = sorted(df['Estado'].dropna().unique()) if 'Estado' in df.columns else []
    selected_states = st.sidebar.multiselect(
        'Estado', state_values, default=[]
    )

    # Filtro de data
    if date_col in df.columns and not df.empty:
        min_date = df[date_col].min().date()
        max_date = df[date_col].max().date()
        start_date, end_date = st.sidebar.date_input(
            'Período', (min_date, max_date), min_value=min_date, max_value=max_date
        )
    else:
        start_date, end_date = None, None

    # Aplicação dos filtros
    filtered_df = df.copy()
    if selected_responsibles:
        filtered_df = filtered_df[filtered_df['Usuário responsável'].isin(selected_responsibles)]
    if selected_categories:
        filtered_df = filtered_df[filtered_df['Categoria'].isin(selected_categories)]
    if selected_states:
        filtered_df = filtered_df[filtered_df['Estado'].isin(selected_states)]
    if start_date and end_date:
        filtered_df = filtered_df[(filtered_df[date_col] >= pd.to_datetime(start_date)) & (filtered_df[date_col] <= pd.to_datetime(end_date))]
    return filtered_df


def display_kpis(df: pd.DataFrame, date_col: str):
    """
    Calcula e exibe os principais indicadores (KPIs) da base filtrada.

    Exibe três métricas principais:
      - Total de registros
      - Número de categorias
      - Novos registros nos últimos 30 dias

    Args:
        df: DataFrame filtrado
        date_col: nome da coluna de data
    """
    total = df.shape[0]
    num_categories = df['Categoria'].nunique() if 'Categoria' in df.columns else 0
    last_30 = 0
    if date_col in df.columns and not df.empty:
        today = pd.Timestamp.now().date()
        threshold = today - pd.Timedelta(days=30)
        last_30 = df[df[date_col] >= pd.to_datetime(threshold)].shape[0]

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric('Total de registros', f'{total}')
    kpi2.metric('Categorias distintas', f'{num_categories}')
    kpi3.metric('Novos (30 dias)', f'{last_30}')


def display_charts(df: pd.DataFrame, date_col: str):
    """
    Cria e exibe gráficos interativos com Plotly.

    - Gráfico de barras para Top 10 Usuário responsável
    - Linha de evolução temporal de registros (escolha de frequência)
    - Barras de distribuição por categoria

    Args:
        df: DataFrame filtrado
        date_col: nome da coluna de data
    """
    if df.empty:
        st.info('Nenhum dado para exibir nos gráficos. Ajuste os filtros acima.')
        return

    # Top responsáveis
    if 'Usuário responsável' in df.columns:
        top_users = df['Usuário responsável'].value_counts().nlargest(10)
        fig_top = px.bar(
            x=top_users.index,
            y=top_users.values,
            labels={'x': 'Usuário responsável', 'y': 'Total'},
            title='Top 10 responsáveis (mais registros)'
        )
        fig_top.update_layout(xaxis_title='', yaxis_title='Total')
    st.plotly_chart(fig_top, width='stretch')

    # Evolução temporal
    if date_col in df.columns:
        # Mapeamento de frequência
        freq_options = {'Mensal': 'ME', 'Semanal': 'W', 'Diária': 'D', 'Trimestral': 'Q'}
        freq_name = st.selectbox('Frequência da série temporal', list(freq_options.keys()))
        freq = freq_options[freq_name]
        counts = (
            df.set_index(date_col)
            .resample(freq)
            .size()
            .reset_index(name='Total')
        )
        fig_time = px.line(
            counts,
            x=date_col,
            y='Total',
            title='Evolução de registros ao longo do tempo'
        )
        fig_time.update_layout(xaxis_title='Data', yaxis_title='Total')
    st.plotly_chart(fig_time, width='stretch')

    # Distribuição por categoria
    if 'Categoria' in df.columns:
        category_counts = df['Categoria'].value_counts().reset_index()
        category_counts.columns = ['Categoria', 'Total']
        fig_cat = px.bar(
            category_counts,
            x='Categoria',
            y='Total',
            title='Distribuição por categoria'
        )
        fig_cat.update_layout(xaxis_title='', yaxis_title='Total')
    st.plotly_chart(fig_cat, width='stretch')


def display_table(df: pd.DataFrame):
    """
    Exibe uma tabela com os dados filtrados.

    Args:
        df: DataFrame filtrado
    """
    st.subheader('Prévia dos dados filtrados')
    st.dataframe(df, width='stretch')


def main():
    st.set_page_config(page_title='Data Sentinel - Delduque', layout='wide')
    st.title('Data Sentinel - Delduque')

    st.markdown(
    'Este painel interativo foi desenvolvido para facilitar a tomada de decisões, '
        'seguindo boas práticas de visualização de dados: conhecer o público e objetivo, '
        'escolher os gráficos adequados, manter a hierarquia visual e focar na clareza.'
    )

    data = load_data('BASE DATA SENTINEL DELDUQUE.xlsx')
    # Apenas abas relevantes para o painel
    sheet_options = [s for s in ['ATIVOS PF E PJ', 'CANCELADOS'] if s in data]
    sheet = st.sidebar.selectbox('Selecionar aba', sheet_options)
    df = data[sheet]
    date_col = 'Data de cadastro' if sheet == 'ATIVOS PF E PJ' else 'Data de saida'
    df = prepare_dataframe(df, date_col)
    filtered_df = filter_dataframe(df, date_col)

    # Exibe os KPIs
    display_kpis(filtered_df, date_col)

    # Exibe gráficos
    display_charts(filtered_df, date_col)

    # Exibe tabela final
    display_table(filtered_df)


if __name__ == '__main__':
    main()
