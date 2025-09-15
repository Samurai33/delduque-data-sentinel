import os
from dotenv import load_dotenv
load_dotenv()
GOOGLE_DRIVE_FILE_ID = os.getenv("GOOGLE_DRIVE_FILE_ID")
from googleapiclient.discovery import build
from google.oauth2 import service_account
import io

# Funções utilitárias modernas
from delduquedatasentinel.utils import (
    prepare_dataframe, filter_dataframe, kpi_total_registros, kpi_num_categorias, kpi_num_estados,
    kpi_ultimos_7_dias, kpi_ultimos_30_dias, kpi_percentual_incompletos, kpi_taxa_crescimento
)

# CSS global moderno
import streamlit as st
st.markdown('''
    <style>
    html, body, [class*="css"]  {
        background-color: #f7f9fa !important;
        color: #222 !important;
        font-family: 'Roboto', 'Lato', 'Segoe UI', Arial, sans-serif !important;
    }
    .stApp { background-color: #f7f9fa; }
    .stButton>button, .stSelectbox, .stTextInput>div>input, .stDataFrame, .stTable {
        border-radius: 8px !important;
    }
    .st-emotion-cache-1v0mbdj { color: #25c5c0 !important; }
    a { color: #25c5c0 !important; }
    </style>
''', unsafe_allow_html=True)

def exportar_sheets_para_xlsx(file_id, destino):
    """
    Exporta uma planilha Google Sheets como .xlsx usando a API do Drive.
    """
    if os.path.exists(destino):
        print(f"Arquivo já existe localmente: {destino}")
        return
    try:
        print(f"Exportando Google Sheets para Excel: {file_id} -> {destino}")
        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        SERVICE_ACCOUNT_FILE = 'credentials.json'
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)
        request = service.files().export_media(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        data = request.execute()
        with open(destino, 'wb') as out_file:
            out_file.write(data)
        print(f"Arquivo exportado com sucesso: {destino}")
    except Exception as e:
        print(f"Erro ao exportar Google Sheets: {e}")
        raise
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




def main():

    # =============================
    # Carregar dados, preparar DataFrame e aplicar filtros antes de qualquer uso
    # =============================
    # Loading animado
    loading_html = '''
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 180px;">
        <svg width="80" height="80" viewBox="0 0 44 44" xmlns="http://www.w3.org/2000/svg" stroke="#25c5c0">
            <g fill="none" fill-rule="evenodd" stroke-width="4">
                <circle cx="22" cy="22" r="18" stroke-opacity=".3"/>
                <path d="M40 22c0-9.94-8.06-18-18-18">
                    <animateTransform attributeName="transform" type="rotate" from="0 22 22" to="360 22 22" dur="1s" repeatCount="indefinite"/>
                </path>
            </g>
        </svg>
        <div style="margin-top: 18px; font-size: 1.3rem; color: #25c5c0; font-weight: 600; letter-spacing: 0.5px;">Carregando dataset seguro...</div>
    </div>
    '''
    loading_placeholder = st.empty()
    loading_placeholder.markdown(loading_html, unsafe_allow_html=True)
    exportar_sheets_para_xlsx(GOOGLE_DRIVE_FILE_ID, 'BASE DELDUQUE DATA SENTINEL.xlsx')
    data = load_data('BASE DELDUQUE DATA SENTINEL.xlsx')
    loading_placeholder.empty()

    # Badge minimalista e pulsante de conexão
    badge_html = '''
    <style>
    .pulse-badge {
        display: inline-flex;
        align-items: center;
        background: #222c24;
        color: #25c5c0;
        border-radius: 18px;
        padding: 0.25rem 1rem 0.25rem 0.6rem;
        font-size: 1rem;
        font-weight: 500;
        box-shadow: 0 1px 6px 0 rgba(36,197,192,0.10);
        margin: 1.2rem 0 0.5rem 0;
        animation: fadeInBadge 1.1s;
    }
    .pulse-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #25c5c0;
        margin-right: 0.6rem;
        box-shadow: 0 0 0 0 #25c5c0;
        animation: pulse 1.2s infinite cubic-bezier(0.66,0,0,1);
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 #25c5c055; }
        70% { box-shadow: 0 0 0 8px #25c5c000; }
        100% { box-shadow: 0 0 0 0 #25c5c000; }
    }
    @keyframes fadeInBadge {
        from { opacity: 0; transform: translateY(-10px);} to { opacity: 1; transform: translateY(0);}
    }
    </style>
    <div class="pulse-badge">
        <span class="pulse-dot"></span>
        Base conectada
    </div>
    '''
    st.markdown(badge_html, unsafe_allow_html=True)

    # Cabeçalho
    st.markdown('<h1 style="font-size:2.6rem; margin-bottom:0.2em; color:#222;">Delduque Data Sentinel</h1>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:1.15rem; color:#444; margin-bottom:1.5em;">Este painel interativo foi desenvolvido para facilitar a tomada de decisões, seguindo boas práticas de visualização de dados: conhecer o público e objetivo, escolher os gráficos adequados, manter a hierarquia visual e focar na clareza.</div>', unsafe_allow_html=True)

    # Carregar e preparar dados
    sheet_options = [s for s in ['ATIVOS PF E PJ', 'CANCELADOS'] if s in data]
    sheet = st.sidebar.selectbox('Selecionar aba', sheet_options, key='aba_select')
    df = data[sheet]
    date_col = 'Data de cadastro' if sheet == 'ATIVOS PF E PJ' else 'Data de saida'
    df = prepare_dataframe(df, date_col)

    # Filtros
    responsible_values = sorted(df['Usuário responsável'].dropna().unique()) if 'Usuário responsável' in df.columns else []
    selected_responsibles = st.sidebar.multiselect('Usuário responsável', responsible_values, default=[], key='responsible_multiselect')
    category_values = sorted(df['Categoria'].dropna().unique()) if 'Categoria' in df.columns else []
    selected_categories = st.sidebar.multiselect('Categoria', category_values, default=[], key='category_multiselect')
    state_values = sorted(df['Estado'].dropna().unique()) if 'Estado' in df.columns else []
    selected_states = st.sidebar.multiselect('Estado', state_values, default=[], key='state_multiselect')
    if date_col in df.columns and not df.empty:
        min_date = df[date_col].min().date()
        max_date = df[date_col].max().date()
        start_date, end_date = st.sidebar.date_input('Período', (min_date, max_date), min_value=min_date, max_value=max_date, key='period_dateinput')
    else:
        start_date, end_date = None, None
    filters = {
        'responsibles': selected_responsibles,
        'categories': selected_categories,
        'states': selected_states,
        'start_date': start_date,
        'end_date': end_date,
        'date_col': date_col
    }
    filtered_df = filter_dataframe(df, filters)

    # =============================
    # Estado dos filtros para cross-filter e reset
    # =============================
    if 'crossfilter' not in st.session_state:
        st.session_state['crossfilter'] = {}
    if 'reset' not in st.session_state:
        st.session_state['reset'] = False

    # Botão de reset de filtros (limpa todos os filtros interativos e cross-filter)
    if st.button('🔄 Reset filtros'):
        st.session_state['crossfilter'] = {}
        st.session_state['reset'] = True
        st.experimental_rerun()

    # Donut (polar) interativo com cross-filter
    if 'Categoria' in filtered_df.columns:
        st.markdown('**Composição percentual por Categoria**')
        cat_counts = filtered_df['Categoria'].value_counts().reset_index()
        cat_counts.columns = ['Categoria', 'Total']
        selected_cat = st.session_state['crossfilter'].get('Categoria')
        fig_donut = px.pie(
            cat_counts,
            names='Categoria',
            values='Total',
            hole=0.55,
            title='',
            color_discrete_sequence=px.colors.sequential.Teal
        )
        fig_donut.update_traces(
            textinfo='none',
            hovertemplate='<b>%{label}</b><br>%{percent:.1%} (%{value:,})<extra></extra>',
            customdata=cat_counts['Total'],
            pull=[0.08 if selected_cat == c else 0 for c in cat_counts['Categoria']],
        )
        fig_donut.update_layout(
            annotations=[dict(text=selected_cat if selected_cat else 'Selecione<br>um setor', x=0.5, y=0.5, font_size=18, showarrow=False, font_color='#25c5c0',
                xanchor='center', yanchor='middle',
                textangle=0, align='center',
            )],
            margin=dict(t=20, b=20, l=0, r=0),
            showlegend=True,
            legend_title_text='Categoria',
            legend=dict(orientation='h', y=-0.15)
        )
        donut_event = st.plotly_chart(fig_donut, use_container_width=True)
        # Cross-filter: clique em setor
        clicked_cat = st.selectbox('Filtrar por categoria (cross-filter)', [''] + cat_counts['Categoria'].tolist(), index=cat_counts['Categoria'].tolist().index(selected_cat) + 1 if selected_cat in cat_counts['Categoria'].tolist() else 0, key='cat_cross')
        if clicked_cat and clicked_cat != selected_cat:
            st.session_state['crossfilter']['Categoria'] = clicked_cat
            st.experimental_rerun()
        elif not clicked_cat and selected_cat:
            st.session_state['crossfilter'].pop('Categoria', None)
            st.experimental_rerun()

    # Barras empilhadas/agrupadas: evolução temporal por segmento com cross-filter
    if date_col in filtered_df.columns and 'Categoria' in filtered_df.columns:
        st.markdown('**Evolução temporal por Categoria**')
        freq = st.radio('Frequência', ['Mensal', 'Semanal'], horizontal=True, key='freq_radio')
        freq_map = {'Mensal': 'M', 'Semanal': 'W'}
        group_mode = st.radio('Modo', ['Empilhado', 'Agrupado'], horizontal=True, key='bar_mode')
        df_time = filtered_df.copy()
        if 'Categoria' in st.session_state['crossfilter']:
            df_time = df_time[df_time['Categoria'] == st.session_state['crossfilter']['Categoria']]
        df_time['Período'] = df_time[date_col].dt.to_period(freq_map[freq]).astype(str)
        bar_data = df_time.groupby(['Período', 'Categoria']).size().reset_index(name='Total')
        fig_bar = px.bar(
            bar_data,
            x='Período',
            y='Total',
            color='Categoria',
            barmode='stack' if group_mode == 'Empilhado' else 'group',
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_bar.update_traces(
            hovertemplate='<b>%{x}</b><br>%{label}: %{y:,}<extra></extra>',
        )
        fig_bar.update_layout(
            xaxis_title='Período',
            yaxis_title='Total',
            margin=dict(t=20, b=20, l=0, r=0),
            legend=dict(orientation='h', y=-0.15)
        )
        bar_event = st.plotly_chart(fig_bar, use_container_width=True)

    # Heatmap: dia da semana × hora (hotspots) com cross-filter
    if date_col in filtered_df.columns:
        st.markdown('**Hotspots: Dia da Semana × Hora**')
        df_heat = filtered_df.copy()
        if 'Categoria' in st.session_state['crossfilter']:
            df_heat = df_heat[df_heat['Categoria'] == st.session_state['crossfilter']['Categoria']]
        df_heat['DiaSemana'] = df_heat[date_col].dt.day_name()
        df_heat['Hora'] = df_heat[date_col].dt.hour
        heatmap_data = df_heat.groupby(['DiaSemana', 'Hora']).size().reset_index(name='Total')
        dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_pivot = heatmap_data.pivot(index='DiaSemana', columns='Hora', values='Total').reindex(dias).fillna(0)
        fig_heat = px.imshow(
            heatmap_pivot,
            aspect='auto',
            color_continuous_scale='teal',
            labels=dict(x='Hora', y='DiaSemana', color='Total'),
            title='',
        )
        fig_heat.update_traces(
            hovertemplate='<b>%{y}</b> às %{x}h<br>%{z:,} registros<extra></extra>',
            selector=dict(type='heatmap'),
        )
        fig_heat.update_layout(margin=dict(t=20, b=20, l=0, r=0))
        heat_event = st.plotly_chart(fig_heat, use_container_width=True)

    # Choropleth: mapa temático por estado (Brasil) com cross-filter
    if 'Estado' in filtered_df.columns:
        st.markdown('**Mapa de Densidade por Estado**')
        uf_ibge = {'AC':12,'AL':27,'AP':16,'AM':13,'BA':29,'CE':23,'DF':53,'ES':32,'GO':52,'MA':21,'MT':51,'MS':50,'MG':31,'PA':15,'PB':25,'PR':41,'PE':26,'PI':22,'RJ':33,'RN':24,'RS':43,'RO':11,'RR':14,'SC':42,'SP':35,'SE':28,'TO':17}
        chorodata = filtered_df['Estado'].value_counts().reset_index()
        chorodata.columns = ['Estado', 'Total']
        chorodata['id'] = chorodata['Estado'].map(uf_ibge)
        selected_uf = st.session_state['crossfilter'].get('Estado')
        if selected_uf:
            chorodata = chorodata[chorodata['Estado'] == selected_uf]
        fig_choro = px.choropleth(
            chorodata,
            locations='id',
            geojson='https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson',
            color='Total',
            hover_name='Estado',
            color_continuous_scale='teal',
            featureidkey='properties.sigla',
            title='',
        )
        fig_choro.update_geos(fitbounds="locations", visible=False)
        fig_choro.update_traces(
            hovertemplate='<b>%{hovertext}</b><br>%{z:,} registros<extra></extra>'
        )
        fig_choro.update_layout(margin=dict(t=20, b=20, l=0, r=0))
        choro_event = st.plotly_chart(fig_choro, use_container_width=True)
        # Cross-filter: selectbox para estado
        estados_disp = filtered_df['Estado'].dropna().unique().tolist()
        clicked_uf = st.selectbox('Filtrar por estado (cross-filter)', [''] + estados_disp, index=estados_disp.index(selected_uf) + 1 if selected_uf in estados_disp else 0, key='uf_cross')
        if clicked_uf and clicked_uf != selected_uf:
            st.session_state['crossfilter']['Estado'] = clicked_uf
            st.experimental_rerun()
        elif not clicked_uf and selected_uf:
            st.session_state['crossfilter'].pop('Estado', None)
            st.experimental_rerun()

    # TODO: Cross-filter e seleção interativa (exemplo de estrutura, precisa de callbacks/State)
    # Se o usuário clicar em um setor do donut, filtrar os outros gráficos por essa categoria
    # Se clicar em uma barra, filtrar por período/categoria
    # Se clicar em um estado no mapa, filtrar por estado
    # Se usar lasso/box no heatmap, filtrar por dia/hora
    # (Implementação completa requer uso de st.session_state e callbacks avançados)
    # Seção de gráficos avançados
    st.markdown('---')
    st.subheader('Visualizações Avançadas')
    if filtered_df.empty:
        st.info('Nenhum dado para exibir nos gráficos. Ajuste os filtros acima.')
        return

    # Gráfico de barras empilhadas: Total por Estado e Categoria
    if 'Estado' in filtered_df.columns and 'Categoria' in filtered_df.columns:
        st.markdown('**Distribuição por Estado e Categoria**')
        stacked = filtered_df.groupby(['Estado', 'Categoria']).size().reset_index(name='Total')
        fig_stacked = px.bar(
            stacked,
            x='Estado',
            y='Total',
            color='Categoria',
            title='Registros por Estado (empilhado por Categoria)',
            barmode='stack',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_stacked.update_layout(xaxis_title='Estado', yaxis_title='Total')
        st.plotly_chart(fig_stacked, use_container_width=True)

    # Donut chart: Distribuição por Categoria
    if 'Categoria' in filtered_df.columns:
        st.markdown('**Distribuição percentual por Categoria**')
        cat_counts = filtered_df['Categoria'].value_counts().reset_index()
        cat_counts.columns = ['Categoria', 'Total']
        fig_donut = px.pie(
            cat_counts,
            names='Categoria',
            values='Total',
            hole=0.5,
            title='Categorias (%)',
            color_discrete_sequence=px.colors.sequential.Teal
        )
        fig_donut.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_donut, use_container_width=True)

    # Heatmap: Registros por mês e estado
    if 'Estado' in filtered_df.columns and date_col in filtered_df.columns:
        st.markdown('**Heatmap de Registros por Mês e Estado**')
        df_heat = filtered_df.copy()
        df_heat['Ano-Mês'] = df_heat[date_col].dt.to_period('M').astype(str)
        heatmap_data = df_heat.groupby(['Ano-Mês', 'Estado']).size().reset_index(name='Total')
        heatmap_pivot = heatmap_data.pivot(index='Ano-Mês', columns='Estado', values='Total').fillna(0)
        fig_heat = px.imshow(
            heatmap_pivot.T,
            aspect='auto',
            color_continuous_scale='teal',
            labels=dict(x='Ano-Mês', y='Estado', color='Total'),
            title='Heatmap: Registros por Mês e Estado'
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # Placeholder para choropleth (mapa): requer coluna de UF ou coordenadas
    # if 'UF' in filtered_df.columns:
    #     ...
    st.set_page_config(page_title='Delduque Data Sentinel', layout='wide')
    st.title('Delduque Data Sentinel')

    st.markdown(
    'Este painel interativo foi desenvolvido para facilitar a tomada de decisões, '
        'seguindo boas práticas de visualização de dados: conhecer o público e objetivo, '
        'escolher os gráficos adequados, manter a hierarquia visual e focar na clareza.'
    )

    # Loading animado
    loading_html = '''
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 180px;">
        <svg width="80" height="80" viewBox="0 0 44 44" xmlns="http://www.w3.org/2000/svg" stroke="#25c5c0">
            <g fill="none" fill-rule="evenodd" stroke-width="4">
                <circle cx="22" cy="22" r="18" stroke-opacity=".3"/>
                <path d="M40 22c0-9.94-8.06-18-18-18">
                    <animateTransform attributeName="transform" type="rotate" from="0 22 22" to="360 22 22" dur="1s" repeatCount="indefinite"/>
                </path>
            </g>
        </svg>
        <div style="margin-top: 18px; font-size: 1.3rem; color: #25c5c0; font-weight: 600; letter-spacing: 0.5px;">Carregando dataset seguro...</div>
    </div>
    '''
    loading_placeholder = st.empty()
    loading_placeholder.markdown(loading_html, unsafe_allow_html=True)
    exportar_sheets_para_xlsx(GOOGLE_DRIVE_FILE_ID, 'BASE DELDUQUE DATA SENTINEL.xlsx')
    data = load_data('BASE DELDUQUE DATA SENTINEL.xlsx')
    loading_placeholder.empty()
    # Badge minimalista e pulsante de conexão
    badge_html = '''
    <style>
    .pulse-badge {
        display: inline-flex;
        align-items: center;
        background: #222c24;
        color: #25c5c0;
        border-radius: 18px;
        padding: 0.25rem 1rem 0.25rem 0.6rem;
        font-size: 1rem;
        font-weight: 500;
        box-shadow: 0 1px 6px 0 rgba(36,197,192,0.10);
        margin: 1.2rem 0 0.5rem 0;
        animation: fadeInBadge 1.1s;
    }
    .pulse-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #25c5c0;
        margin-right: 0.6rem;
        box-shadow: 0 0 0 0 #25c5c0;
        animation: pulse 1.2s infinite cubic-bezier(0.66,0,0,1);
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 #25c5c055; }
        70% { box-shadow: 0 0 0 8px #25c5c000; }
        100% { box-shadow: 0 0 0 0 #25c5c000; }
    }
    @keyframes fadeInBadge {
        from { opacity: 0; transform: translateY(-10px);} to { opacity: 1; transform: translateY(0);}
    }
    </style>
    <div class="pulse-badge">
        <span class="pulse-dot"></span>
        Base conectada
    </div>
    '''
    st.markdown(badge_html, unsafe_allow_html=True)

    # Cabeçalho
    st.markdown('<h1 style="font-size:2.6rem; margin-bottom:0.2em; color:#222;">Delduque Data Sentinel</h1>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:1.15rem; color:#444; margin-bottom:1.5em;">Este painel interativo foi desenvolvido para facilitar a tomada de decisões, seguindo boas práticas de visualização de dados: conhecer o público e objetivo, escolher os gráficos adequados, manter a hierarquia visual e focar na clareza.</div>', unsafe_allow_html=True)

    # Carregar e preparar dados
    sheet_options = [s for s in ['ATIVOS PF E PJ', 'CANCELADOS'] if s in data]
    # (Removido: chamada duplicada de selectbox para aba)
    df = data[sheet]
    date_col = 'Data de cadastro' if sheet == 'ATIVOS PF E PJ' else 'Data de saida'
    df = prepare_dataframe(df, date_col)

    # Filtros
    responsible_values = sorted(df['Usuário responsável'].dropna().unique()) if 'Usuário responsável' in df.columns else []
    selected_responsibles = st.sidebar.multiselect('Usuário responsável', responsible_values, default=[])
    category_values = sorted(df['Categoria'].dropna().unique()) if 'Categoria' in df.columns else []
    selected_categories = st.sidebar.multiselect('Categoria', category_values, default=[])
    state_values = sorted(df['Estado'].dropna().unique()) if 'Estado' in df.columns else []
    selected_states = st.sidebar.multiselect('Estado', state_values, default=[])
    if date_col in df.columns and not df.empty:
        min_date = df[date_col].min().date()
        max_date = df[date_col].max().date()
        start_date, end_date = st.sidebar.date_input('Período', (min_date, max_date), min_value=min_date, max_value=max_date)
    else:
        start_date, end_date = None, None
    filters = {
        'responsibles': selected_responsibles,
        'categories': selected_categories,
        'states': selected_states,
        'start_date': start_date,
        'end_date': end_date,
        'date_col': date_col
    }
    filtered_df = filter_dataframe(df, filters)

    # Linha de KPIs moderna
    kpi_cols = st.columns(6)
    kpi_cols[0].metric('Total de registros', kpi_total_registros(filtered_df))
    kpi_cols[1].metric('Categorias distintas', kpi_num_categorias(filtered_df))
    kpi_cols[2].metric('Estados distintos', kpi_num_estados(filtered_df))
    kpi_cols[3].metric('Novos (7 dias)', kpi_ultimos_7_dias(filtered_df, date_col))
    kpi_cols[4].metric('Novos (30 dias)', kpi_ultimos_30_dias(filtered_df, date_col))
    kpi_cols[5].metric('% incompletos', f"{kpi_percentual_incompletos(filtered_df)}%")
    # Taxa de crescimento (exemplo: mensal)
    st.caption(f"Taxa de crescimento (mensal): {kpi_taxa_crescimento(filtered_df, date_col, 'M')}%")
    # (Removido: chamada duplicada de filtros e preparação de dados)

    # Exibe tabela final
    st.subheader('Prévia dos dados filtrados')
    st.dataframe(filtered_df, width='stretch')


if __name__ == '__main__':
    main()
