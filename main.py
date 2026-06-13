import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px


# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="최근 1년 주가 분석",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# -----------------------------
# Tickers
# -----------------------------
TICKERS = {
    "삼성전자": "005930.KS",
    "하이닉스": "000660.KS",
    "구글": "GOOGL",
    "MS": "MSFT",
    "애플": "AAPL",
    "테슬라": "TSLA",
}
DISPLAY_ORDER = list(TICKERS.keys())


# -----------------------------
# Theme system
# -----------------------------
THEMES = {
    "화이트 모드": {
        "bg": "#ffffff",
        "fg": "#111827",
        "card": "#f8fafc",
        "card2": "#eef2f7",
        "border": "#e5e7eb",
        "muted": "#6b7280",
        "accent": "#2563eb",
        "accent_soft": "rgba(37, 99, 235, 0.12)",
        "template": "plotly_white",
        "plot": ["#2563eb", "#7c3aed", "#059669", "#f59e0b", "#ef4444", "#0ea5e9"],
    },
    "다크 모드": {
        "bg": "#0f1117",
        "fg": "#f5f7fa",
        "card": "#171b26",
        "card2": "#1d2330",
        "border": "#2b3240",
        "muted": "#9aa4b2",
        "accent": "#60a5fa",
        "accent_soft": "rgba(96, 165, 250, 0.14)",
        "template": "plotly_dark",
        "plot": ["#60a5fa", "#c084fc", "#34d399", "#fbbf24", "#f87171", "#22d3ee"],
    },
}


def apply_theme(mode: str) -> dict:
    """Inject theme-specific CSS and return theme tokens."""
    t = THEMES[mode]

    st.markdown(
        f"""
        <style>
            .stApp {{
                background: {t['bg']};
                color: {t['fg']};
            }}

            .main .block-container {{
                padding-top: 0.6rem;
                padding-bottom: 2rem;
                max-width: 1300px;
            }}

            .sticky-hero {{
                position: sticky;
                top: 0;
                z-index: 999;
                background: linear-gradient(180deg, {t['bg']} 84%, {t['bg']}f0 100%);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                padding: 0.65rem 0 0.8rem 0;
                border-bottom: 1px solid {t['border']};
                margin-bottom: 0.4rem;
            }}

            .hero-title {{
                font-size: clamp(1.55rem, 3.4vw, 2.4rem);
                font-weight: 900;
                letter-spacing: -0.03em;
                line-height: 1.08;
                margin: 0;
                color: {t['fg']};
            }}

            .hero-sub {{
                margin-top: 0.35rem;
                color: {t['muted']};
                font-size: 0.95rem;
            }}

            .theme-badge {{
                display: inline-block;
                margin-top: 0.45rem;
                padding: 0.28rem 0.7rem;
                border-radius: 999px;
                background: {t['accent_soft']};
                color: {t['fg']};
                font-size: 0.82rem;
                font-weight: 700;
            }}

            .summary-card {{
                background: {t['card']};
                border: 1px solid {t['border']};
                border-radius: 20px;
                padding: 1rem 1.1rem;
                box-shadow: 0 8px 24px rgba(0,0,0,0.05);
                margin-bottom: 0.7rem;
            }}

            .summary-title {{
                font-size: 0.88rem;
                color: {t['muted']};
                margin-bottom: 0.25rem;
                font-weight: 700;
            }}

            .summary-value {{
                font-size: 1.35rem;
                font-weight: 900;
                line-height: 1.28;
                margin: 0;
                color: {t['fg']};
            }}

            .summary-sub {{
                color: {t['muted']};
                font-size: 0.83rem;
                margin-top: 0.3rem;
            }}

            .section-note {{
                color: {t['muted']};
                font-size: 0.9rem;
                margin-top: -0.4rem;
                margin-bottom: 0.8rem;
            }}

            [data-testid="stMetric"] {{
                background: {t['card']};
                border: 1px solid {t['border']};
                border-radius: 18px;
                padding: 0.65rem 0.8rem;
                box-shadow: 0 4px 18px rgba(0,0,0,0.03);
            }}

            [data-testid="stMetricLabel"] {{
                color: {t['muted']};
            }}

            [data-testid="stDataFrame"] {{
                border-radius: 18px;
                overflow: hidden;
                border: 1px solid {t['border']};
            }}

            [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
                background-color: {t['card']};
                border-color: {t['border']};
                color: {t['fg']};
                border-radius: 14px;
            }}

            [data-testid="stSelectbox"] div[data-baseweb="select"] input {{
                color: {t['fg']};
            }}

            [data-testid="stRadio"] label {{
                color: {t['fg']};
            }}

            [data-testid="stRadio"] [role="radiogroup"] {{
                gap: 0.35rem;
            }}

            div[data-baseweb="popover"] {{
                background: {t['card']};
                color: {t['fg']};
            }}

            div[data-testid="stSidebar"] {{
                background: {t['bg']};
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    return t


# -----------------------------
# Data loading
# -----------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_close_series(ticker: str):
    """최근 1년 종가를 안전하게 가져와서 Series로 반환합니다."""
    try:
        df = yf.download(
            ticker,
            period="1y",
            auto_adjust=True,
            progress=False,
            threads=False,
        )
    except Exception:
        return None

    if df is None or df.empty or "Close" not in df.columns:
        return None

    close = df["Close"]

    # yfinance / pandas 조합에 따라 Close가 DataFrame으로 오는 경우가 있어서 안전하게 처리합니다.
    if isinstance(close, pd.DataFrame):
        if close.shape[1] == 0:
            return None
        close = close.iloc[:, 0]

    close = pd.Series(close).dropna().copy()
    close.index = pd.to_datetime(close.index)
    return close


@st.cache_data(ttl=3600, show_spinner=False)
def load_price_frame() -> pd.DataFrame:
    """모든 종목의 종가를 하나의 DataFrame으로 합칩니다."""
    series_list = []

    for name, ticker in TICKERS.items():
        s = fetch_close_series(ticker)
        if s is not None and not s.empty:
            s = s.copy()
            s.name = name
            series_list.append(s)

    if not series_list:
        return pd.DataFrame()

    return pd.concat(series_list, axis=1).sort_index()


# -----------------------------
# Calculations
# -----------------------------
def calc_period_return(series: pd.Series):
    """최근 1년 누적 수익률을 계산합니다."""
    s = series.dropna()
    if len(s) < 2:
        if len(s) == 1:
            return 0.0, float(s.iloc[-1]), s.index[0], s.index[0]
        return 0.0, 0.0, pd.NaT, pd.NaT

    first = float(s.iloc[0])
    last = float(s.iloc[-1])
    pct = (last / first - 1) * 100
    return pct, last, s.index[0], s.index[-1]



def calc_day_change(series: pd.Series):
    """최근 거래일 기준 전일 대비 변동률을 계산합니다."""
    s = series.dropna()
    if len(s) < 2:
        if len(s) == 1:
            last = float(s.iloc[-1])
            return 0.0, last, last, s.index[-1], s.index[-1]
        return 0.0, 0.0, 0.0, pd.NaT, pd.NaT

    prev = float(s.iloc[-2])
    last = float(s.iloc[-1])
    pct = (last / prev - 1) * 100
    return pct, prev, last, s.index[-2], s.index[-1]



def format_signed_pct(pct: float) -> str:
    return f"{pct:+.2f}%"


# -----------------------------
# UI
# -----------------------------
mode = st.radio(
    "화면 모드를 선택해 주세요.",
    ["화이트 모드", "다크 모드"],
    horizontal=True,
    index=0,
    label_visibility="collapsed",
)

T = apply_theme(mode)

st.markdown(
    f"""
    <div class="sticky-hero">
        <div class="hero-title">📈 최근 1년 주가 변동 분석</div>
        <div class="hero-sub">삼성전자 · 하이닉스 · 구글 · MS · 애플 · 테슬라의 최근 1년 흐름을 한 번에 비교해요.</div>
        <div class="theme-badge">현재 모드: {mode}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.spinner("주가 데이터를 불러오는 중이에요..."):
    price_df = load_price_frame()

if price_df.empty:
    st.error("주가 데이터를 불러오지 못했어요. 네트워크 상태나 티커 설정을 확인해 주세요.")
    st.stop()


# -----------------------------
# Summary data
# -----------------------------
summary_rows = []
for col in price_df.columns:
    day_pct, prev_close, last_close, prev_dt, last_dt = calc_day_change(price_df[col])
    year_pct, year_last, year_start_dt, year_end_dt = calc_period_return(price_df[col])
    summary_rows.append(
        {
            "종목": col,
            "오늘변동률": day_pct,
            "전일종가": prev_close,
            "최근종가": last_close,
            "최근1년수익률": year_pct,
            "1년시작일": year_start_dt,
            "1년종료일": year_end_dt,
            "전일기준일": prev_dt,
            "최근기준일": last_dt,
        }
    )

summary_df = pd.DataFrame(summary_rows).sort_values("최근1년수익률", ascending=False).reset_index(drop=True)


# -----------------------------
# Header cards
# -----------------------------
selected_name = st.selectbox("종목을 선택해 주세요.", DISPLAY_ORDER, index=0)
selected_row = summary_df.loc[summary_df["종목"] == selected_name].iloc[0]
selected_day_pct = float(selected_row["오늘변동률"])
selected_year_pct = float(selected_row["최근1년수익률"])
selected_last = float(selected_row["최근종가"])
selected_prev = float(selected_row["전일종가"])

main_word = "상승" if selected_day_pct >= 0 else "하락"
main_arrow = "📈" if selected_day_pct >= 0 else "📉"
trend_color = T["accent"] if selected_day_pct >= 0 else ("#ef4444" if mode == "화이트 모드" else "#f87171")

left, right = st.columns([1.35, 1])

with left:
    st.markdown(
        f"""
        <div class="summary-card">
            <div class="summary-title">오늘 기준 변동</div>
            <div class="summary-value" style="color:{trend_color};">
                {main_arrow} 오늘 '{selected_name}' 주식은 {format_signed_pct(selected_day_pct)} {main_word}했어요!
            </div>
            <div class="summary-sub">최근 거래일 종가와 그 전 거래일 종가를 기준으로 계산했어요.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        f"""
        <div class="summary-card">
            <div class="summary-title">최근 1년 누적 변동</div>
            <div class="summary-value">{format_signed_pct(selected_year_pct)}</div>
            <div class="summary-sub">최근 1년 첫 거래일과 가장 최근 거래일을 기준으로 계산했어요.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# Metrics
# -----------------------------
st.markdown("### 종목별 한눈에 보기")
st.markdown(
    "<div class='section-note'>오늘 변동률과 최근 1년 누적 수익률을 같이 확인할 수 있어요.</div>",
    unsafe_allow_html=True,
)

metric_cols = st.columns(6)
for i, row in summary_df.iterrows():
    name = row["종목"]
    day_pct = float(row["오늘변동률"])
    year_pct = float(row["최근1년수익률"])
    last_close = float(row["최근종가"])

    metric_cols[i % 6].metric(
        label=name,
        value=f"{day_pct:+.2f}%",
        delta=f"1년: {year_pct:+.2f}% / 종가: {last_close:,.2f}",
    )


# -----------------------------
# Ranking table
# -----------------------------
st.markdown("### 최근 1년 수익률 순위")
rank_df = summary_df.copy()
rank_df["오늘변동률"] = rank_df["오늘변동률"].map(lambda x: round(float(x), 2))
rank_df["최근1년수익률"] = rank_df["최근1년수익률"].map(lambda x: round(float(x), 2))
rank_df["최근종가"] = rank_df["최근종가"].map(lambda x: round(float(x), 2))
rank_df["전일종가"] = rank_df["전일종가"].map(lambda x: round(float(x), 2))
rank_df["1년시작일"] = rank_df["1년시작일"].dt.strftime("%Y-%m-%d")
rank_df["1년종료일"] = rank_df["1년종료일"].dt.strftime("%Y-%m-%d")
rank_df["전일기준일"] = rank_df["전일기준일"].dt.strftime("%Y-%m-%d")
rank_df["최근기준일"] = rank_df["최근기준일"].dt.strftime("%Y-%m-%d")

st.dataframe(
    rank_df[
        [
            "종목",
            "오늘변동률",
            "최근1년수익률",
            "최근종가",
            "전일종가",
            "1년시작일",
            "1년종료일",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)


# -----------------------------
# Selected stock chart
# -----------------------------
st.markdown("### 선택한 종목의 최근 1년 그래프")
selected_series = price_df[selected_name].dropna().copy()
selected_chart = selected_series.reset_index()
selected_chart.columns = ["날짜", "종가"]

fig = px.line(
    selected_chart,
    x="날짜",
    y="종가",
    title=f"{selected_name} 최근 1년 주가 흐름",
    template=T["template"],
    labels={"날짜": "날짜", "종가": "주가"},
    color_discrete_sequence=T["plot"],
)
fig.update_traces(mode="lines", line=dict(width=3))
fig.update_layout(
    hovermode="x unified",
    margin=dict(l=20, r=20, t=60, b=20),
    height=540,
    paper_bgcolor=T["bg"],
    plot_bgcolor=T["bg"],
    font=dict(color=T["fg"]),
    title=dict(font=dict(color=T["fg"])),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    xaxis=dict(gridcolor=T["border"], zerolinecolor=T["border"], linecolor=T["border"]),
    yaxis=dict(gridcolor=T["border"], zerolinecolor=T["border"], linecolor=T["border"]),
)
st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Normalized comparison chart
# -----------------------------
st.markdown("### 전체 종목 비교 그래프")
st.markdown(
    "<div class='section-note'>첫 거래일을 100으로 맞춰서 상대적인 움직임을 비교할 수 있어요.</div>",
    unsafe_allow_html=True,
)

norm_df = price_df.copy()
for col in norm_df.columns:
    s = norm_df[col].dropna()
    if len(s) > 0:
        norm_df[col] = norm_df[col] / s.iloc[0] * 100

norm_reset = norm_df.reset_index()
date_col = norm_reset.columns[0]
chart_df = norm_reset.rename(columns={date_col: "Date"}).melt(
    id_vars="Date",
    var_name="종목",
    value_name="기준=100",
).dropna()

fig2 = px.line(
    chart_df,
    x="Date",
    y="기준=100",
    color="종목",
    title="최근 1년 정규화 주가 추이 (첫 거래일 = 100)",
    template=T["template"],
    labels={"Date": "날짜", "기준=100": "정규화 가격"},
    color_discrete_sequence=T["plot"],
)
fig2.update_layout(
    hovermode="x unified",
    margin=dict(l=20, r=20, t=60, b=20),
    height=620,
    legend_title_text="종목",
    paper_bgcolor=T["bg"],
    plot_bgcolor=T["bg"],
    font=dict(color=T["fg"]),
    title=dict(font=dict(color=T["fg"])),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    xaxis=dict(gridcolor=T["border"], zerolinecolor=T["border"], linecolor=T["border"]),
    yaxis=dict(gridcolor=T["border"], zerolinecolor=T["border"], linecolor=T["border"]),
)
st.plotly_chart(fig2, use_container_width=True)


# -----------------------------
# Footer summary
# -----------------------------
best_row = summary_df.iloc[0]
worst_row = summary_df.iloc[-1]

st.info(
    f"가장 많이 오른 종목은 **{best_row['종목']} ({best_row['최근1년수익률']:+.2f}%)** 이고, "
    f"가장 덜 오른 종목은 **{worst_row['종목']} ({worst_row['최근1년수익률']:+.2f}%)** 이에요."
)

st.caption(
    "수익률은 자동 조정된 종가(auto_adjust=True)를 사용해서 계산했어요. 데이터가 없는 날은 가장 최근 거래일 기준으로 표시했어요."
)
