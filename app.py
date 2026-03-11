import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pykrx import stock

st.set_page_config(page_title="Stock Radar", page_icon="📈", layout="wide")

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.6rem; padding-bottom: 2rem; max-width: 1200px;}
    .stButton>button {border-radius: 14px; height: 46px; font-weight: 700;}
    .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
        border-radius: 24px;
        padding: 24px 28px;
        margin-bottom: 18px;
    }
    .card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 16px 18px;
        margin-bottom: 14px;
    }
    .pill {
        display:inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        border: 1px solid #e5e7eb;
        background:#f8fafc;
        font-size: 0.82rem;
        margin-right: 6px;
        margin-top: 6px;
    }
    .muted {color:#6b7280; font-size:0.92rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

THEMES = {
    "반도체": ["삼성전자", "SK하이닉스", "한미반도체", "리노공업", "테크윙", "이수페타시스", "피에스케이홀딩스"],
    "AI": ["이수페타시스", "NAVER", "카카오", "삼성에스디에스", "폴라리스오피스"],
    "방산": ["한화에어로스페이스", "LIG넥스원", "현대로템", "한국항공우주"],
    "원전": ["두산에너빌리티", "한전기술", "비에이치아이", "우리기술"],
    "조선": ["HD한국조선해양", "한화오션", "삼성중공업", "HD현대중공업"],
    "2차전지": ["에코프로비엠", "에코프로", "포스코퓨처엠", "엘앤에프"],
    "로봇": ["레인보우로보틱스", "두산로보틱스", "로보스타", "유일로보틱스"],
    "전력기기": ["HD현대일렉트릭", "LS ELECTRIC", "효성중공업", "제룡전기"],
}

ETF_THEME_RULES = {
    "반도체": ["반도체", "필라델피아"],
    "AI": ["AI", "인공지능", "빅테크", "테크"],
    "방산": ["방산", "디펜스"],
    "원전": ["원전", "원자력", "SMR"],
    "조선": ["조선", "해운"],
    "2차전지": ["2차전지", "배터리", "전기차"],
    "로봇": ["로봇", "자동화"],
    "전력기기": ["전력", "인프라", "전선", "전력설비"],
}

MODE_RULES = {
    "정상": "최대 3종목",
    "중립": "최대 2종목",
    "방어": "최대 1종목 · 현금 비중 확대",
}

if "stock_results" not in st.session_state:
    st.session_state.stock_results = pd.DataFrame()
if "etf_results" not in st.session_state:
    st.session_state.etf_results = pd.DataFrame()


def prev_business_day() -> str:
    d = datetime.now()
    if d.hour < 8:
        d = d - timedelta(days=1)
    while d.weekday() >= 5:
        d = d - timedelta(days=1)
    return d.strftime("%Y%m%d")


def start_lookback(days: int = 40) -> str:
    d = datetime.now() - timedelta(days=days)
    return d.strftime("%Y%m%d")


def infer_stock_theme(name: str):
    for theme, names in THEMES.items():
        if name in names:
            return theme
    return None


def infer_etf_theme(name: str):
    for theme, keywords in ETF_THEME_RULES.items():
        if any(k.lower() in name.lower() for k in keywords):
            return theme
    return None


def result_card(rank: int, name: str, theme: str, score: int, reasons: list[str], risk: str):
    pills = "".join([f"<span class='pill'>{r}</span>" for r in reasons])
    st.markdown(
        f"""
        <div class='card'>
            <div style='display:flex;justify-content:space-between;align-items:flex-start;gap:12px;'>
                <div>
                    <div class='muted'>#{rank} · {theme}</div>
                    <div style='font-size:1.16rem;font-weight:800;margin-top:2px'>{name}</div>
                </div>
                <div style='font-size:1.12rem;font-weight:800'>{score}</div>
            </div>
            <div style='margin-top:10px'>{pills}</div>
            <div class='muted' style='margin-top:10px'>주의 · {risk}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=60 * 60 * 4, show_spinner=False)
def get_stock_universe(base_date: str) -> pd.DataFrame:
    kospi_ohlcv = stock.get_market_ohlcv_by_ticker(base_date, market="KOSPI")
    kosdaq_ohlcv = stock.get_market_ohlcv_by_ticker(base_date, market="KOSDAQ")
    kospi_cap = stock.get_market_cap_by_ticker(base_date, market="KOSPI")
    kosdaq_cap = stock.get_market_cap_by_ticker(base_date, market="KOSDAQ")

    kospi = kospi_ohlcv.join(kospi_cap[["시가총액"]], how="left")
    kosdaq = kosdaq_ohlcv.join(kosdaq_cap[["시가총액"]], how="left")
    df = pd.concat([kospi, kosdaq], axis=0).reset_index().rename(columns={"티커": "ticker"})
    df["name"] = df["ticker"].apply(stock.get_market_ticker_name)
    df["theme"] = df["name"].apply(infer_stock_theme)
    df = df[df["theme"].notna()].copy()
    return df


@st.cache_data(ttl=60 * 60 * 4, show_spinner=False)
def get_etf_universe(base_date: str) -> pd.DataFrame:
    df = stock.get_etf_ohlcv_by_ticker(base_date).reset_index().rename(columns={"티커": "ticker"})
    df["name"] = df["ticker"].apply(stock.get_etf_ticker_name)
    df["theme"] = df["name"].apply(infer_etf_theme)
    df = df[df["theme"].notna()].copy()
    return df


@st.cache_data(ttl=60 * 60 * 4, show_spinner=False)
def get_price_history(ticker: str, is_etf: bool = False) -> pd.DataFrame:
    s = start_lookback(70)
    e = prev_business_day()
    if is_etf:
        df = stock.get_etf_ohlcv_by_date(s, e, ticker)
    else:
        df = stock.get_market_ohlcv_by_date(s, e, ticker)
    return df


@st.cache_data(ttl=60 * 60 * 4, show_spinner=False)
def build_stock_candidates() -> tuple[pd.DataFrame, dict]:
    base_date = prev_business_day()
    uni = get_stock_universe(base_date)
    debug = {"universe": int(len(uni)), "liq_pass": 0, "price_pass": 0, "final_pass": 0}
    rows = []

    for _, row in uni.iterrows():
        value = float(row.get("거래대금", 0) or 0)
        mcap = float(row.get("시가총액", 0) or 0)
        if value < 100_000_000_000 or mcap < 1_500_000_000_000:
            continue
        debug["liq_pass"] += 1

        hist = get_price_history(row["ticker"], is_etf=False)
        if hist.empty or len(hist) < 25:
            continue
        close = hist["종가"].iloc[-1]
        ma20 = hist["종가"].rolling(20).mean().iloc[-1]
        ma20_prev = hist["종가"].rolling(20).mean().iloc[-2]
        if pd.isna(ma20) or close <= ma20:
            continue
        debug["price_pass"] += 1

        ret_5d = ((close / hist["종가"].iloc[-6]) - 1) * 100 if len(hist) >= 6 else 0
        if ret_5d >= 30:
            continue

        recent_high_10 = hist["고가"].tail(10).max()
        near_breakout = close >= recent_high_10 * 0.98

        score = 0
        reasons = []

        if value >= 300_000_000_000:
            score += 20
            reasons.append("거래대금 강함")
        else:
            score += 12
            reasons.append("거래대금 양호")

        if close > ma20 and ma20 > ma20_prev:
            score += 15
            reasons.append("20일선 우위")
        else:
            score += 8

        if near_breakout:
            score += 15
            reasons.append("고점 근접")

        chg_pct = float(row.get("등락률", 0) or 0)
        if abs(chg_pct) >= 3:
            score += 10
            reasons.append("상대강도")

        score += 10
        reasons.append("핵심 테마")

        risk = "단기 과열 확인" if ret_5d >= 15 else "20일선 유지 확인"
        rows.append(
            {
                "name": row["name"],
                "theme": row["theme"],
                "score": int(score),
                "reasons": reasons[:4],
                "risk": risk,
                "value": value,
            }
        )

    df = pd.DataFrame(rows).sort_values(["score", "value"], ascending=[False, False]).reset_index(drop=True) if rows else pd.DataFrame()
    debug["final_pass"] = int(len(df))
    return df, debug


@st.cache_data(ttl=60 * 60 * 4, show_spinner=False)
def build_etf_candidates() -> pd.DataFrame:
    base_date = prev_business_day()
    uni = get_etf_universe(base_date)
    rows = []

    for _, row in uni.iterrows():
        value = float(row.get("거래대금", 0) or 0)
        if value < 30_000_000_000:
            continue

        hist = get_price_history(row["ticker"], is_etf=True)
        if hist.empty or len(hist) < 25:
            continue
        close = hist["종가"].iloc[-1]
        ma20 = hist["종가"].rolling(20).mean().iloc[-1]
        if pd.isna(ma20) or close <= ma20:
            continue

        ret_5d = ((close / hist["종가"].iloc[-6]) - 1) * 100 if len(hist) >= 6 else 0
        if ret_5d >= 25:
            continue

        score = 0
        reasons = []

        if value >= 100_000_000_000:
            score += 20
            reasons.append("거래대금 강함")
        else:
            score += 12
            reasons.append("거래대금 양호")

        score += 20
        reasons.append("20일선 우위")

        if ret_5d > 0:
            score += 15
            reasons.append("5일 수익률")

        if row["theme"] in ["반도체", "AI", "전력기기", "방산", "원전"]:
            score += 15
            reasons.append("핵심 테마")

        risk = "섹터 변동성 확인" if ret_5d >= 10 else "추세 유지 확인"
        rows.append(
            {
                "name": row["name"],
                "theme": row["theme"],
                "score": int(score),
                "reasons": reasons[:4],
                "risk": risk,
                "value": value,
            }
        )

    return pd.DataFrame(rows).sort_values(["score", "value"], ascending=[False, False]).reset_index(drop=True) if rows else pd.DataFrame()


st.sidebar.title("Stock Radar")
page = st.sidebar.radio("", ["대시보드", "자동 발굴", "조건"], label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.caption(datetime.now().strftime("%Y-%m-%d %H:%M"))

st.markdown(
    """
    <div class='hero'>
        <div style='font-size:0.92rem;opacity:0.82'>국내주식 · 국내상장 ETF · 오전 1회</div>
        <div style='font-size:2rem;font-weight:800;margin-top:6px'>Stock Radar</div>
        <div style='margin-top:10px;opacity:0.9'>TOP 5 자동 발굴</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if page == "대시보드":
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("시장", "2", "국내 · ETF")
    with c2:
        st.metric("후보", "TOP 5", "우선순위")
    with c3:
        st.metric("기간", "스윙·중기")
    with c4:
        st.metric("테마", "8")

    left, right = st.columns(2)
    with left:
        st.markdown("### 국내주식")
        if st.session_state.stock_results.empty:
            st.caption("실행 전")
        else:
            for i, row in st.session_state.stock_results.head(5).iterrows():
                result_card(i + 1, row["name"], row["theme"], row["score"], row["reasons"], row["risk"])
    with right:
        st.markdown("### ETF")
        if st.session_state.etf_results.empty:
            st.caption("실행 전")
        else:
            for i, row in st.session_state.etf_results.head(5).iterrows():
                result_card(i + 1, row["name"], row["theme"], row["score"], row["reasons"], row["risk"])

elif page == "자동 발굴":
    col1, col2 = st.columns([1.05, 0.95])
    with col1:
        market_mode = st.selectbox("시장 모드", list(MODE_RULES.keys()))
        term = st.selectbox("기간", ["스윙", "중기"])
        selected_themes = st.multiselect("테마", list(THEMES.keys()), default=list(THEMES.keys()))
        run = st.button("종목 발굴 실행", type="primary", use_container_width=True)
    with col2:
        st.info(MODE_RULES[market_mode])
        st.markdown("- 필수 · 거래대금 / 20일선 / 테마 / 시총")
        st.markdown("- 가점 · 거래대금 강도 / 고점 근접 / 상대강도")
        st.markdown("- 제외 · 최근 급등 / 저유동성 / 20일선 하회")

    if run:
        with st.spinner("국내주식 수집 중"):
            stock_df, stock_debug = build_stock_candidates()
        with st.spinner("ETF 수집 중"):
            etf_df = build_etf_candidates()

        if not stock_df.empty:
            stock_df = stock_df[stock_df["theme"].isin(selected_themes)].head(5).copy()
        if not etf_df.empty:
            etf_df = etf_df[etf_df["theme"].isin(selected_themes)].head(5).copy()

        st.session_state.stock_results = stock_df
        st.session_state.etf_results = etf_df
        st.session_state.stock_debug = stock_debug

    if "stock_debug" in st.session_state:
        with st.expander("진단"):
            st.write(st.session_state.stock_debug)

    st.markdown("### 국내주식 TOP 5")
    if st.session_state.stock_results.empty:
        st.caption("결과 없음")
    else:
        for i, row in st.session_state.stock_results.iterrows():
            result_card(i + 1, row["name"], row["theme"], row["score"], row["reasons"], row["risk"])

    st.markdown("### ETF TOP 5")
    if st.session_state.etf_results.empty:
        st.caption("결과 없음")
    else:
        for i, row in st.session_state.etf_results.iterrows():
            result_card(i + 1, row["name"], row["theme"], row["score"], row["reasons"], row["risk"])

elif page == "조건":
    st.markdown("### 필수 조건")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("- 국내주식 거래대금 1000억 원 이상")
        st.markdown("- 국내주식 시총 1.5조 원 이상")
        st.markdown("- 종가 > 20일선")
        st.markdown("- 핵심 테마 포함")
    with c2:
        st.markdown("- ETF 거래대금 300억 원 이상")
        st.markdown("- 종가 > 20일선")
        st.markdown("- 최근 급등 제외")
        st.markdown("- 핵심 테마 포함")

    st.markdown("### 감시 테마")
    st.markdown(" · ".join(THEMES.keys()))
