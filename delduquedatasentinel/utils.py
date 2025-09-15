import pandas as pd
from typing import Dict, Any

def prepare_dataframe(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """
    Converte a coluna de data para datetime e remove registros sem data.
    Utilizado para garantir consistência temporal nas análises.
    Args:
        df: DataFrame original
        date_col: nome da coluna de data
    Returns:
        DataFrame com coluna de data formatada e sem nulos
    """
    df = df.copy()
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
    return df

def filter_dataframe(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Aplica filtros de usuário, categoria, estado e período ao DataFrame.
    Os filtros são passados via dicionário e permitem filtragem dinâmica.
    Args:
        df: DataFrame original
        filters: dicionário com listas de valores e datas
    Returns:
        DataFrame filtrado conforme os critérios
    """
    filtered_df = df.copy()
    if filters.get('responsibles'):
        filtered_df = filtered_df[filtered_df['Usuário responsável'].isin(filters['responsibles'])]
    if filters.get('categories'):
        filtered_df = filtered_df[filtered_df['Categoria'].isin(filters['categories'])]
    if filters.get('states'):
        filtered_df = filtered_df[filtered_df['Estado'].isin(filters['states'])]
    if filters.get('start_date') and filters.get('end_date'):
        filtered_df = filtered_df[(filtered_df[filters['date_col']] >= pd.to_datetime(filters['start_date'])) & (filtered_df[filters['date_col']] <= pd.to_datetime(filters['end_date']))]
    return filtered_df

def kpi_total_registros(df: pd.DataFrame) -> int:
    """
    Retorna o total de registros do DataFrame.
    """
    return df.shape[0]

def kpi_num_categorias(df: pd.DataFrame) -> int:
    """
    Retorna o número de categorias distintas.
    """
    return df['Categoria'].nunique() if 'Categoria' in df.columns else 0

def kpi_num_estados(df: pd.DataFrame) -> int:
    """
    Retorna o número de estados distintos.
    """
    return df['Estado'].nunique() if 'Estado' in df.columns else 0

def kpi_ultimos_7_dias(df: pd.DataFrame, date_col: str) -> int:
    """
    Retorna o número de registros nos últimos 7 dias.
    """
    if date_col in df.columns and not df.empty:
        today = pd.Timestamp.now().date()
        threshold = today - pd.Timedelta(days=7)
        return df[df[date_col] >= pd.to_datetime(threshold)].shape[0]
    return 0

def kpi_ultimos_30_dias(df: pd.DataFrame, date_col: str) -> int:
    """
    Retorna o número de registros nos últimos 30 dias.
    """
    if date_col in df.columns and not df.empty:
        today = pd.Timestamp.now().date()
        threshold = today - pd.Timedelta(days=30)
        return df[df[date_col] >= pd.to_datetime(threshold)].shape[0]
    return 0

def kpi_percentual_incompletos(df: pd.DataFrame, campos_relevantes=None) -> float:
    """
    Calcula o percentual de registros com pelo menos um campo relevante em branco.
    Args:
        df: DataFrame
        campos_relevantes: lista de colunas consideradas essenciais
    Returns:
        Percentual de registros incompletos (0-100)
    """
    if campos_relevantes is None:
        campos_relevantes = ['Usuário responsável', 'Categoria', 'Estado']
    if not all(col in df.columns for col in campos_relevantes):
        return 0.0
    incompletos = df[campos_relevantes].isnull().any(axis=1).sum()
    total = len(df)
    return round((incompletos / total) * 100, 2) if total > 0 else 0.0

def kpi_taxa_crescimento(df: pd.DataFrame, date_col: str, freq: str = 'M') -> float:
    """
    Calcula a taxa de crescimento percentual entre os dois últimos períodos.
    Args:
        df: DataFrame
        date_col: coluna de data
        freq: frequência ('M'=mensal, 'W'=semanal)
    Returns:
        Taxa de crescimento percentual (float)
    """
    if date_col not in df.columns or df.empty:
        return 0.0
    counts = df.set_index(date_col).resample(freq).size()
    if len(counts) < 2:
        return 0.0
    anterior, atual = counts.iloc[-2], counts.iloc[-1]
    if anterior == 0:
        return 0.0
    return round(((atual - anterior) / anterior) * 100, 2)
