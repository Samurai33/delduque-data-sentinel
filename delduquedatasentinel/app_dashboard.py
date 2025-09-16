"""
app_dashboard.py

Painel Streamlit modular com tema escuro, Plotly charts e filtragem cruzada.

Contém a função pública criar_dashboard(dataframe) que monta todo o layout.
"""
from typing import Dict, Optional, List
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Optional: better plotly event capture
try:
    from streamlit_plotly_events import plotly_events
    HAS_PLOTLY_EVENTS = True
except (ImportError, ModuleNotFoundError):
    HAS_PLOTLY_EVENTS = False

# Theme colors
DARK_BG = "#1e1e2e"
DARK_TEXT = "#e0e0e0"
CARD_BG = "#262635"
CARD_BORDER = "rgba(255,255,255,0.06)"

def inject_streamlit_css():
    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: {DARK_BG}; color: {DARK_TEXT}; }}
        .css-1d391kg {{ background-color: {DARK_BG} !important; }}
        .card {{ background: linear-gradient(180deg, {CARD_BG}, {DARK_BG}); border: 1px solid {CARD_BORDER}; border-radius: 8px; padding: 14px; margin-bottom: 16px; }}
        .card-title {{ color: {DARK_TEXT}; font-weight: 600; margin-bottom: 8px; font-size: 16px; }}
        .stDataFrame thead tr th {{ background-color: rgba(255,255,255,0.06) !important; color: {DARK_TEXT} !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def make_plotly_dark_template() -> Dict:
    layout = dict(
        font=dict(color=DARK_TEXT, family="Inter, Roboto, Arial"),
        paper_bgcolor=DARK_BG,
        plot_bgcolor=DARK_BG,
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=40, r=20, t=60, b=40),
        hoverlabel=dict(bgcolor="#2b2b3a", font=dict(color=DARK_TEXT)),
    )
    return layout

PLOTLY_LAYOUT_DEFAULTS = make_plotly_dark_template()

# Approximate centroids for Brazil states (siglas)
BRAZIL_UF_CENTROIDS = {
    "AC": (-8.77, -70.55), "AL": (-9.62, -36.82), "AM": (-3.07, -61.66),
    "AP": (1.41, -51.77), "BA": (-12.96, -38.51), "CE": (-5.20, -39.53),
    "DF": (-15.83, -47.86), "ES": (-20.31, -40.34), "GO": (-16.64, -49.31),
    "MA": (-5.54, -45.56), "MG": (-18.10, -44.38), "MS": (-20.51, -54.54),
    "MT": (-12.64, -55.42), "PA": (-5.53, -52.29), "PB": (-7.06, -35.55),
    "PE": (-8.28, -35.07), "PI": (-7.71, -42.73), "PR": (-24.89, -51.55),
    "RJ": (-22.27, -42.91), "RN": (-5.22, -36.52), "RO": (-11.22, -62.80),
    "RR": (1.89, -61.22), "RS": (-30.01, -52.10), "SC": (-27.33, -49.44),
    "SE": (-10.83, -37.95), "SP": (-22.19, -48.79), "TO": (-9.65, -48.26)
}

def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], errors="coerce")
    else:
        raise ValueError("DataFrame must contain 'data' column (dates).")
    if "valor" in df.columns:
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0.0)
    else:
        raise ValueError("DataFrame must contain 'valor' column (numeric).")
    if "dow" not in df.columns:
        df["dow"] = df["data"].dt.day_name().fillna("Unknown")
    else:
        df["dow"] = df["dow"].astype(str)
    if "hora" not in df.columns:
        if df["data"].dt.hour.notnull().any():
            df["hora"] = df["data"].dt.hour.fillna(0).astype(int)
        else:
            df["hora"] = 0
    else:
        df["hora"] = pd.to_numeric(df["hora"], errors="coerce").fillna(0).astype(int)
    if "categoria" not in df.columns:
        df["categoria"] = "Unknown"
    if "regiao" not in df.columns:
        df["regiao"] = "Unknown"
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    if df["dow"].isin(dow_order).any():
        df["dow"] = pd.Categorical(df["dow"], categories=dow_order, ordered=True)
    return df

def reset_filters_in_session():
    for k in [
        "filter_categoria", "filter_dates", "filter_regioes",
        "filter_dow", "filter_hora", "plotly_selection"
    ]:
        if k in st.session_state:
            del st.session_state[k]

def render_sidebar_filters(df: pd.DataFrame) -> Dict:
    st.sidebar.header("Filtros")
    min_date, max_date = df["data"].min(), df["data"].max()
    date_range = st.sidebar.date_input("Intervalo de datas", value=(min_date.date(), max_date.date()))
    categorias = sorted(df["categoria"].dropna().unique().tolist())
    selected_categorias = st.sidebar.multiselect("Categorias", options=categorias, default=categorias)
    regioes = sorted(df["regiao"].dropna().unique().tolist())
    selected_regioes = st.sidebar.multiselect("Regiões (UF)", options=regioes, default=regioes)
    dow_options = df["dow"].unique().tolist()
    selected_dow = st.sidebar.multiselect("Dia da semana", options=dow_options, default=dow_options)
    min_h, max_h = int(df["hora"].min()), int(df["hora"].max())
    hora_range = st.sidebar.slider("Hora (intervalo)", min_value=min_h, max_value=max_h, value=(min_h, max_h))
    st.sidebar.markdown("---")
    stacked_mode = st.sidebar.radio("Modo barras", ("Empilhado", "Agrupado"))
    show_legend = st.sidebar.checkbox("Mostrar legenda", value=True)
    st.sidebar.markdown("---")
    if st.sidebar.button("Reset filtros"):
        reset_filters_in_session()
        st.experimental_rerun()
    return dict(
        date_range=date_range,
        categorias=selected_categorias,
        regioes=selected_regioes,
        dow=selected_dow,
        hora_range=hora_range,
        stacked_mode=stacked_mode,
        show_legend=show_legend,
    )

def build_donut_figure(df: pd.DataFrame) -> go.Figure:
    agg = df.groupby("categoria", as_index=False)["valor"].sum().sort_values("valor", ascending=False)
    fig = px.pie(agg, names="categoria", values="valor", hole=0.45, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(title_text="Participação por categoria", **PLOTLY_LAYOUT_DEFAULTS)
    fig.update_traces(textinfo="percent+label", hovertemplate="%{label}: %{value} (%{percent})")
    return fig

def build_stacked_or_grouped_bars(df: pd.DataFrame, mode: str = "Empilhado") -> go.Figure:
    df_agg = df.groupby([pd.Grouper(key="data", freq="D"), "categoria"], as_index=False)["valor"].sum()
    pivot = df_agg.pivot(index="data", columns="categoria", values="valor").fillna(0)
    categories = pivot.columns.tolist()
    fig = go.Figure()
    for cat in categories:
        fig.add_trace(go.Bar(x=pivot.index, y=pivot[cat], name=str(cat)))
    if mode == "Empilhado":
        fig.update_layout(barmode="stack")
    else:
        fig.update_layout(barmode="group")
    fig.update_xaxes(tickangle=-45)
    fig.update_layout(title_text="Evolução temporal por categoria", **PLOTLY_LAYOUT_DEFAULTS)
    return fig

def build_heatmap_scatter(df: pd.DataFrame) -> go.Figure:
    agg = df.groupby(["dow", "hora"], as_index=False, observed=True)["valor"].sum()
    size = (agg["valor"] - agg["valor"].min())
    if size.max() > 0:
        size = 8 + (size / size.max()) * 38
    else:
        size = np.full(len(agg), 8)
    fig = px.scatter(agg, x="hora", y="dow", size=size, color="valor", color_continuous_scale=px.colors.sequential.Inferno, hover_data={"valor": True, "hora": True, "dow": True})
    fig.update_traces(marker=dict(line=dict(width=0.5, color="rgba(255,255,255,0.06)")))
    fig.update_layout(title_text="Heatmap (dia da semana × hora) — selecione com lasso", dragmode="lasso", **PLOTLY_LAYOUT_DEFAULTS)
    fig.update_xaxes(title_text="Hora")
    fig.update_yaxes(title_text="Dia da semana")
    return fig

def build_region_map(df: pd.DataFrame) -> go.Figure:
    agg = df.groupby("regiao", as_index=False)["valor"].sum()
    agg["lat"] = agg["regiao"].map(lambda r: BRAZIL_UF_CENTROIDS.get(r, (np.nan, np.nan))[0])
    agg["lon"] = agg["regiao"].map(lambda r: BRAZIL_UF_CENTROIDS.get(r, (np.nan, np.nan))[1])
    if agg["lat"].isna().all():
        fig = px.bar(agg.sort_values("valor", ascending=False), x="regiao", y="valor", color="valor", color_continuous_scale=px.colors.sequential.Plasma)
        fig.update_layout(title_text="Regiões (mapa indisponível — exiba como barras)", **PLOTLY_LAYOUT_DEFAULTS)
        return fig
    fig = px.scatter_geo(agg, lat="lat", lon="lon", size="valor", hover_name="regiao", projection="natural earth", scope="south america", color="valor", color_continuous_scale=px.colors.sequential.Viridis)
    fig.update_layout(title_text="Mapa por UF (tamanho = valor agregado)", **PLOTLY_LAYOUT_DEFAULTS)
    fig.update_geos(bgcolor=DARK_BG, lakecolor=DARK_BG)
    return fig

def capture_plotly_event(fig: go.Figure, height: int = 350, key: Optional[str] = None) -> List[dict]:
    if HAS_PLOTLY_EVENTS:
        events = plotly_events(fig, select_event=True, override_height=height, key=key)
        return events or []
    else:
        st.plotly_chart(fig, width="stretch")
        return []

def criar_dashboard(dataframe: pd.DataFrame):
    st.set_page_config(page_title="Painel — Dark UI", layout="wide")
    inject_streamlit_css()
    df = prepare_dataframe(dataframe)
    filters = render_sidebar_filters(df)
    df_filtered = df[(df["data"].dt.date >= pd.to_datetime(filters["date_range"][0]).date()) & (df["data"].dt.date <= pd.to_datetime(filters["date_range"][1]).date()) & (df["categoria"].isin(filters["categorias"])) & (df["regiao"].isin(filters["regioes"])) & (df["dow"].isin(filters["dow"])) & (df["hora"] >= filters["hora_range"][0]) & (df["hora"] <= filters["hora_range"][1])].copy()

    st.markdown("<div style='display:flex; align-items:center; justify-content:space-between;'><h2 style='color:%s'>Painel Analítico</h2><div style='color:%s'>Tema escuro • Interatividade: clique nos gráficos</div></div>" % (DARK_TEXT, "#9aa0b3"), unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Donut — participação por categoria</div>", unsafe_allow_html=True)
        donut_fig = build_donut_figure(df_filtered)
        donut_events = capture_plotly_event(donut_fig, height=360, key="donut")
        selected_categoria = None
        if donut_events:
            ev = donut_events[0]
            if "label" in ev:
                selected_categoria = ev["label"]
            elif "points" in ev and len(ev["points"]) > 0:
                p = ev["points"][0]
                selected_categoria = p.get("label") or p.get("x") or None
        if selected_categoria:
            st.session_state["filter_categoria"] = selected_categoria
        if selected_categoria or "filter_categoria" in st.session_state:
            cur = st.session_state.get("filter_categoria")
            st.markdown(f"<div style='color:{DARK_TEXT}; margin-top:8px'>Selecionado: <b>{cur}</b></div>", unsafe_allow_html=True)
            if st.button("Limpar seleção (categoria)"):
                st.session_state.pop("filter_categoria", None)
                st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Barras temporais</div>", unsafe_allow_html=True)
        mode = filters["stacked_mode"]
        bars_fig = build_stacked_or_grouped_bars(df_filtered, mode=mode)
        bars_events = capture_plotly_event(bars_fig, height=360, key="bars")
        if bars_events:
            ev = bars_events[0]
            if "x" in ev:
                try:
                    clicked_date = pd.to_datetime(ev["x"]).date()
                    st.session_state["filter_dates"] = clicked_date
                except Exception:
                    pass
        st.markdown("<div style='color:#9aa0b3; margin-top:8px;'>Clique numa barra para filtrar por data (quando disponível).</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    col3, col4 = st.columns([1.5, 1.5], gap="large")
    with col3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Heatmap — dia da semana × hora</div>", unsafe_allow_html=True)
        heatmap_fig = build_heatmap_scatter(df_filtered)
        heat_events = capture_plotly_event(heatmap_fig, height=440, key="heatmap")
        if heat_events:
            selected_points = []
            for ev in heat_events:
                pts = ev.get("points") or []
                for p in pts:
                    selected_points.append((p.get("y"), p.get("x")))
            if selected_points:
                st.session_state["heatmap_selection"] = selected_points
        if "heatmap_selection" in st.session_state:
            st.markdown(f"<div style='color:{DARK_TEXT}; margin-top:8px'>Heatmap selecionado: {len(st.session_state['heatmap_selection'])} pontos</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col4:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Mapa — valores por UF</div>", unsafe_allow_html=True)
        map_fig = build_region_map(df_filtered)
        map_events = capture_plotly_event(map_fig, height=440, key="map")
        if map_events:
            ev = map_events[0]
            if "points" in ev and len(ev["points"]) > 0:
                p = ev["points"][0]
                hover = p.get("hovertext") or p.get("customdata") or None
                if hover:
                    st.session_state["filter_regiao_click"] = hover
        st.markdown("</div>", unsafe_allow_html=True)

    df_cross = df_filtered.copy()
    if "filter_categoria" in st.session_state:
        cat = st.session_state["filter_categoria"]
        df_cross = df_cross[df_cross["categoria"] == cat]
    if "filter_dates" in st.session_state:
        clicked_date = st.session_state["filter_dates"]
        if isinstance(clicked_date, (datetime, pd.Timestamp, pd.Series)):
            clicked_date = pd.to_datetime(clicked_date).date()
        df_cross = df_cross[df_cross["data"].dt.date == clicked_date]
    if "heatmap_selection" in st.session_state:
        sel = st.session_state["heatmap_selection"]
        sel_set = set(sel)
        df_cross = df_cross[df_cross.apply(lambda r: (r["dow"], r["hora"]) in sel_set, axis=1)]
    if "filter_regiao_click" in st.session_state:
        region_clicked = st.session_state["filter_regiao_click"]
        df_cross = df_cross[df_cross["regiao"].astype(str).str.contains(str(region_clicked), na=False)]

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    lower_col1, lower_col2 = st.columns([1.5, 1], gap="large")
    with lower_col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Resumo</div>", unsafe_allow_html=True)
        total_val = df_cross["valor"].sum()
        records = len(df_cross)
        st.markdown(f"<div style='font-size:28px; font-weight:700; color:{DARK_TEXT}'>R$ {total_val:,.2f}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:#9aa0b3'>Registros: {records}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with lower_col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Detalhes — tabela filtrada</div>", unsafe_allow_html=True)
        display_df = df_cross.sort_values(by="data", ascending=False).reset_index(drop=True)
        show_cols = ["data", "categoria", "regiao", "hora", "dow", "valor"]
        show_cols = [c for c in show_cols if c in display_df.columns]
        display_df_small = display_df[show_cols].copy()
        if "data" in display_df_small.columns:
            display_df_small["data"] = display_df_small["data"].dt.strftime("%Y-%m-%d %H:%M:%S")
        try:
            styled = (display_df_small.style
                      .set_table_styles([
                          {"selector": "thead", "props": [("background-color", "rgba(255,255,255,0.06)"), ("color", DARK_TEXT), ("font-weight", "600")]},
                          {"selector": "tbody tr:nth-child(odd)", "props": [("background-color", "rgba(255,255,255,0.02)")]},
                          {"selector": "tbody tr:nth-child(even)", "props": [("background-color", "transparent")]},
                      ])
                      .format({"valor": "{:,.2f}"}))
            st.dataframe(styled, width="stretch", height=360)
        except Exception:
            # Fallback if Streamlit version doesn't accept Styler
            st.dataframe(display_df_small, width="stretch", height=360)
        st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("Sobre este painel e dependências"):
        st.markdown("""
            - O painel usa Plotly para visualizações; para captura direta de cliques e seleção nos gráficos é recomendado instalar `streamlit-plotly-events` (opcional).
            - Dependências mínimas: `streamlit`, `pandas`, `plotly`, `numpy`.
            - Se o mapa não mostrar corretamente, verifique o conteúdo da coluna `regiao` (use siglas UF ou forneça `lat`,`lon`).
            """)

if __name__ == "__main__":
    st.title("Demo: Painel Dark UI - Demo de dados sintéticos")
    uploaded = st.file_uploader("Carregar CSV (opcional) — colunas esperadas: data,categoria,regiao,valor,dow,hora", type=["csv"])
    if uploaded:
        df_in = pd.read_csv(uploaded)
    else:
        rng = pd.date_range(end=pd.Timestamp.now(), periods=300, freq="H")
        categorias = ["A", "B", "C", "D"]
        regioes = list(BRAZIL_UF_CENTROIDS.keys())
        rnd = np.random.default_rng(123)
        df_in = pd.DataFrame({
            "data": rnd.choice(rng, size=1000),
            "categoria": rnd.choice(categorias, size=1000),
            "regiao": rnd.choice(regioes, size=1000),
            "valor": rnd.exponential(scale=120.0, size=1000).round(2),
        })
        df_in["dow"] = df_in["data"].dt.day_name()
        df_in["hora"] = df_in["data"].dt.hour
    criar_dashboard(df_in)
