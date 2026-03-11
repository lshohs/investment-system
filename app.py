import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from functools import lru_cache
import re
import time

st.set_page_config(page_title="Stock Radar", page_icon="📈", layout="wide")

# =========================
# Style
# =========================
st.markdown(
    """
    <style>
    .block-container {padding-top: 1.6rem; padding-bottom: 2rem; max-width: 1220px;}
    .stButton>button {border-radius: 14px; height: 46px; font-weight: 700;}
    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiSelect div[data-baseweb="select"] > div,
    .stTextInput input {
        border-radius: 14px !important;
    }
    .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
        border-radius: 24px;
        padding: 26px 28px;
        margin-bottom: 18px;
    }
    .card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 16px 18px;
        margin-bottom: 14px;
    }
    .metric-card {
        background: linear-gradient(180deg,#ffffff 0%, #f8fafc 100%);
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 16px;
    }
    .muted {color:#6b7280; font-size:0.92rem;}
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
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# Constants
# =========================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Referer": "https://finance.naver.com/",
}
REQUEST_TIMEOUT = 15
MARKETS = ["국내주식", "국내상장 ETF"]
TERMS = ["스윙", "중기"]
MARKET_MODES = ["정상", "중립", "방어"]

THEME_KEYWORDS = {
    "반도체": ["반도체", "HBM", "메모리", "파운드리", "장비", "테스트", "후공정"],
    "AI": ["AI", "인공지능", "서버", "데이터센터", "클라우드", "GPU", "NPU"],
    "방산": ["방산", "미사일", "군수", "방위", "레이더", "우주항공"],
    "원전": ["원전", "원자력", "SMR", "핵연료", "원자로"],
    "조선": ["조선", "해양", "선박", "LNG선", "조선기자재"],
    "2차전지": ["2차전지", "배터리", "양극재", "음극재", "전해질", "리튬"],
    "로봇": ["로봇", "협동로봇", "자동화", "모빌리티로봇"],
    "전력기기": ["전력", "변압기", "배전", "전선", "전력기기", "초고압", "전력설비"],
}

STOCK_THEME_MAP = {
    "한미반도체": "반도체",
    "이수페타시스": "AI",
    "리노공업": "반도체",
    "테크윙": "반도체",
    "피에스케이홀딩스": "반도체",
    "LIG넥스원": "방산",
    "한화에어로스페이스": "방산",
    "현대로템": "방산",
    "두산에너빌리티": "원전",
    "비에이치아이": "원전",
    "한전기술": "원전",
    "HD현대일렉트릭": "전력기기",
    "LS ELECTRIC": "전력기기",
    "효성중공업": "전력기기",
    "HD한국조선해양": "조선",
    "한화오션": "조선",
    "삼성중공업": "조선",
    "에코프로비엠": "2차전지",
    "포스코퓨처엠": "2차전지",
    "에코프로": "2차전지",
    "레인보우로보틱스": "로봇",
    "두산로보틱스": "로봇",
    "로보스타": "로봇",
    "삼성전자": "반도체",
    "SK하이닉스": "반도체",
}

ETF_THEME_RULES = {
    "반도체": ["반도체", "SOXX", "필라델피아"],
    "AI": ["AI", "인공지능", "빅테크", "테크"],
    "방산": ["방산", "디펜스"],
    "원전": ["원전", "원자력", "SMR"],
    "조선": ["조선", "해운"],
    "2차전지": ["2차전지", "배터리", "전기차"],
    "로봇": ["로봇", "자동화"],
    "전력기기": ["전력", "전선", "전력설비", "인프라"],
}

if "results_stock" not in st.session_state:
    st.session_state.results_stock = pd.DataFrame()
if "results_etf" not in st.session_state:
    st.session_state.results_etf = pd.DataFrame()
if "last_run_msg" not in st.session_state:
    st.session_state.last_run_msg = ""

# =========================
# Helpers
# =========================
def parse_number(value):
    if pd.isna(value):
        return None
    text = str(value).strip()
    text = text.replace(",", "")
    text = text.replace("%", "")
    text = text.replace("N/A", "")
    if text in ["", "-"]:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def clean_name(name: str) -> str:
    return re.sub(r"\s+", " ", str(name)).strip()


def infer_theme_stock(name: str) -> str | None:
    if name in STOCK_THEME_MAP:
        return STOCK_THEME_MAP[name]
    for theme, keywords in THEME_KEYWORDS.items():
        if any(k.lower() in name.lower() for k in keywords):
            return theme
    return None


def infer_theme_etf(name: str) -> str | None:
    for theme, keywords in ETF_THEME_RULES.items():
        if any(k.lower() in name.lower() for k in keywords):
            return theme
    return None


def result_card(item: dict):
    reasons = "".join([f"<span class='pill'>{r}</span>" for r in item["reasons"]])
    st.markdown(
        f"""
        <div class='card'>
            <div style='display:flex;justify-content:space-between;align-items:flex-start;gap:12px;'>
                <div>
                    <div class='muted'>#{item['rank']} · {item['theme']}</div>
                    <div style='font-size:1.14rem;font-weight:700;margin-top:2px'>{item['name']}</div>
                </div>
                <div style='font-size:1.15rem;font-weight:800'>{item['score']}</div>
            </div>
            <div style='margin-top:10px'>{reasons}</div>
            <div class='muted' style='margin-top:12px'>주의 · {item['risk']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# Naver collectors
# =========================
@st.cache_data(ttl=60 * 60 * 4, show_spinner=False)
def fetch_market_sum(sosok: int = 0, pages: int = 4) -> pd.DataFrame:
    rows = []
    for page in range(1, pages + 1):
        url = f"https://finance.naver.com/sise/sise_market_sum.naver?sosok={sosok}&page={page}"
        try:
            tables = pd.read_html(url, encoding="euc-kr")
        except Exception:
            continue
        if not tables:
            continue
        df = tables[1].copy() if len(tables) > 1 else tables[0].copy()
        df = df.dropna(how="all")
        if "종목명" not in df.columns:
            continue
        df = df[df["종목명"].notna()].copy()
        rows.append(df)
        time.sleep(0.15)
    if not rows:
        return pd.DataFrame()
    out = pd.concat(rows, ignore_index=True)
    out = out[[c for c in out.columns if c in ["종목명", "현재가", "등락률", "거래량", "거래대금", "시가총액", "토론실"]]].copy()
    out = out.rename(columns={"종목명": "name", "현재가": "close", "등락률": "chg_pct", "거래량": "volume", "거래대금": "value", "시가총액": "mcap"})
    out["name"] = out["name"].map(clean_name)
    out["close"] = out["close"].map(parse_number)
    out["chg_pct"] = out["chg_pct"].map(parse_number)
    out["volume"] = out["volume"].map(parse_number)
    out["value"] = out["value"].map(parse_number)
    out["mcap"] = out["mcap"].map(parse_number)
    out = out.drop_duplicates(subset=["name"])
    return out


@st.cache_data(ttl=60 * 60 * 4, show_spinner=False)
def fetch_etf_list() -> pd.DataFrame:
    url = "https://finance.naver.com/sise/etf.naver"
    try:
        tables = pd.read_html(url, encoding="euc-kr")
    except Exception:
        return pd.DataFrame()
    target = None
    for t in tables:
        if "종목명" in t.columns:
            target = t.copy()
            break
    if target is None:
        return pd.DataFrame()
    target = target.dropna(how="all")
    target = target[target["종목명"].notna()].copy()
    cols = [c for c in target.columns if c in ["종목명", "현재가", "등락률", "거래량", "거래대금", "NAV", "3개월수익률", "1개월수익률"]]
    target = target[cols].copy()
    target = target.rename(columns={"종목명": "name", "현재가": "close", "등락률": "chg_pct", "거래량": "volume", "거래대금": "value", "3개월수익률": "ret_3m", "1개월수익률": "ret_1m"})
    for col in ["close", "chg_pct", "volume", "value", "ret_3m", "ret_1m"]:
        if col in target.columns:
            target[col] = target[col].map(parse_number)
    target["name"] = target["name"].map(clean_name)
    target = target.drop_duplicates(subset=["name"])
    return target


@lru_cache(maxsize=512)
def resolve_stock_code(name: str) -> str | None:
    for sosok in [0, 1]:
        url = f"https://finance.naver.com/sise/sise_market_sum.naver?sosok={sosok}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            resp.encoding = "euc-kr"
        except Exception:
            continue
        soup = BeautifulSoup(resp.text, "lxml")
        links = soup.select("a.tltle")
        for a in links:
            if clean_name(a.get_text()) == name:
                href = a.get("href", "")
                m = re.search(r"code=(\d+)", href)
                if m:
                    return m.group(1)
    return None


@st.cache_data(ttl=60 * 60 * 4, show_spinner=False)
def fetch_daily_prices(code: str, pages: int = 5) -> pd.DataFrame:
    frames = []
    for page in range(1, pages + 1):
        url = f"https://finance.naver.com/item/sise_day.naver?code={code}&page={page}"
        try:
            tables = pd.read_html(url, encoding="euc-kr")
        except Exception:
            continue
        if not tables:
            continue
        df = tables[0].copy().dropna()
        if "날짜" not in df.columns:
            continue
        df["날짜"] = pd.to_datetime(df["날짜"])
        for col in ["종가", "시가", "고가", "저가", "거래량"]:
            df[col] = df[col].map(parse_number)
        frames.append(df)
        time.sleep(0.1)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["날짜"]).sort_values("날짜")
    return out


@st.cache_data(ttl=60 * 60 * 4, show_spinner=False)
def fetch_recent_news_count(code: str, pages: int = 2, recent_days: int = 3) -> int:
    count = 0
    threshold = datetime.now() - timedelta(days=recent_days)
    for page in range(1, pages + 1):
        url = f"https://finance.naver.com/item/news_news.naver?code={code}&page={page}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            resp.encoding = "euc-kr"
        except Exception:
            continue
        soup = BeautifulSoup(resp.text, "lxml")
        dates = soup.select("table.type5 td.date")
        for d in dates:
            text = d.get_text(strip=True)
            try:
                dt = datetime.strptime(text, "%Y.%m.%d %H:%M")
            except Exception:
                continue
            if dt >= threshold:
                count += 1
        time.sleep(0.1)
    return count


# =========================
# Scoring engine
# =========================
def calc_stock_metrics(row: pd.Series) -> dict | None:
    code = resolve_stock_code(row["name"])
    if not code:
        return None
    price_df = fetch_daily_prices(code, pages=6)
    if price_df.empty or len(price_df) < 25:
        return None

    price_df = price_df.sort_values("날짜")
    close = price_df["종가"].iloc[-1]
    ma20 = price_df["종가"].rolling(20).mean().iloc[-1]
    ma20_prev = price_df["종가"].rolling(20).mean().iloc[-2]
    ret_5d = ((close / price_df["종가"].iloc[-6]) - 1) * 100 if len(price_df) >= 6 else 0
    high_10 = price_df["고가"].tail(10).max()
    near_breakout = close >= high_10 * 0.98
    news_count = fetch_recent_news_count(code, pages=2, recent_days=3)

    theme = infer_theme_stock(row["name"])
    if not theme:
        return None

    return {
        "code": code,
        "theme": theme,
        "close": close,
        "ma20": ma20,
        "ma20_up": ma20 > ma20_prev,
        "ret_5d": ret_5d,
        "near_breakout": near_breakout,
        "news_count": news_count,
    }


@st.cache_data(ttl=60 * 60 * 4, show_spinner=False)
def build_stock_candidates() -> pd.DataFrame:
    kospi = fetch_market_sum(0, pages=4)
    kosdaq = fetch_market_sum(1, pages=4)
    universe = pd.concat([kospi, kosdaq], ignore_index=True)
    universe = universe.dropna(subset=["name", "close", "value", "mcap"]).copy()

    results = []
    progress_placeholder = st.empty()
    names = universe["name"].tolist()
    for idx, name in enumerate(names[:120]):  # 1차 버전: 상위 유동성 종목 중심
        progress_placeholder.caption(f"국내주식 수집 중 {idx+1}/120")
        row = universe.loc[universe["name"] == name].iloc[0]
        theme = infer_theme_stock(name)
        if not theme:
            continue
        if (row["value"] or 0) < 300 or (row["mcap"] or 0) < 2000:
            continue
        metrics = calc_stock_metrics(row)
        if not metrics:
            continue
        if metrics["close"] <= metrics["ma20"]:
            continue
        if metrics["ret_5d"] >= 25:
            continue
        if metrics["news_count"] < 1:
            continue

        score = 0
        reasons = []

        if row["value"] >= 800:
            score += 20
            reasons.append("거래대금 강함")
        elif row["value"] >= 500:
            score += 14
            reasons.append("거래대금 양호")
        else:
            score += 8

        if metrics["close"] > metrics["ma20"] and metrics["ma20_up"]:
            score += 15
            reasons.append("20일선 우위")
        elif metrics["close"] > metrics["ma20"]:
            score += 10

        if metrics["near_breakout"]:
            score += 15
            reasons.append("고점 근접")

        if metrics["news_count"] >= 5:
            score += 10
            reasons.append("뉴스 강도")
        elif metrics["news_count"] >= 2:
            score += 6
            reasons.append("뉴스 유지")

        if abs(row.get("chg_pct", 0) or 0) >= 3:
            score += 10
            reasons.append("상대강도")

        # 테마 대표 종목 가점
        if name in STOCK_THEME_MAP:
            score += 10
            reasons.append("핵심 테마주")

        risk = "단기 과열 확인" if metrics["ret_5d"] >= 15 else "20일선 유지 확인"

        results.append(
            {
                "name": name,
                "theme": metrics["theme"],
                "score": int(score),
                "value": row["value"],
                "mcap": row["mcap"],
                "chg_pct": row.get("chg_pct", 0),
                "news_count": metrics["news_count"],
                "ret_5d": metrics["ret_5d"],
                "risk": risk,
                "reasons": reasons[:4],
            }
        )
    progress_placeholder.empty()
    if not results:
        return pd.DataFrame()
    df = pd.DataFrame(results).sort_values(["score", "value"], ascending=[False, False]).reset_index(drop=True)
    return df


@st.cache_data(ttl=60 * 60 * 4, show_spinner=False)
def build_etf_candidates() -> pd.DataFrame:
    df = fetch_etf_list()
    if df.empty:
        return pd.DataFrame()
    df["theme"] = df["name"].apply(infer_theme_etf)
    df = df[df["theme"].notna()].copy()
    df = df[df["value"].fillna(0) >= 100].copy()

    rows = []
    for _, row in df.iterrows():
        score = 0
        reasons = []

        if row["value"] >= 300:
            score += 20
            reasons.append("거래대금 강함")
        elif row["value"] >= 150:
            score += 14
            reasons.append("거래대금 양호")
        else:
            score += 8

        ret_1m = row.get("ret_1m", 0) or 0
        ret_3m = row.get("ret_3m", 0) or 0
        if ret_1m > 0:
            score += 20
            reasons.append("1개월 수익률")
        if ret_3m > 0:
            score += 15
            reasons.append("3개월 수익률")
        if abs(row.get("chg_pct", 0) or 0) >= 1.5:
            score += 15
            reasons.append("상대강도")
        if row["theme"] in ["반도체", "AI", "전력기기", "방산", "원전"]:
            score += 15
            reasons.append("핵심 테마")

        risk = "섹터 변동성 확인" if row["chg_pct"] and abs(row["chg_pct"]) > 3 else "추세 유지 확인"
        rows.append(
            {
                "name": row["name"],
                "theme": row["theme"],
                "score": int(score),
                "value": row["value"],
                "chg_pct": row.get("chg_pct", 0),
                "risk": risk,
                "reasons": reasons[:4],
            }
        )
    return pd.DataFrame(rows).sort_values(["score", "value"], ascending=[False, False]).reset_index(drop=True)


# =========================
# Layout
# =========================
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
        st.markdown("<div class='metric-card'><div class='muted'>시장</div><div style='font-size:1.4rem;font-weight:800;margin-top:4px'>2</div><div class='muted' style='margin-top:6px'>국내주식 · ETF</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='metric-card'><div class='muted'>후보</div><div style='font-size:1.4rem;font-weight:800;margin-top:4px'>TOP 5</div><div class='muted' style='margin-top:6px'>우선순위 출력</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='metric-card'><div class='muted'>기간</div><div style='font-size:1.4rem;font-weight:800;margin-top:4px'>스윙 · 중기</div><div class='muted' style='margin-top:6px'>오전 1회</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown("<div class='metric-card'><div class='muted'>테마</div><div style='font-size:1.4rem;font-weight:800;margin-top:4px'>8</div><div class='muted' style='margin-top:6px'>핵심 테마</div></div>", unsafe_allow_html=True)

    st.markdown("### 최근 결과")
    left, right = st.columns(2)
    with left:
        st.markdown("#### 국내주식")
        stock_df = st.session_state.results_stock
        if stock_df.empty:
            st.caption("실행 전")
        else:
            for i, row in stock_df.head(5).iterrows():
                result_card({"rank": i + 1, "name": row["name"], "theme": row["theme"], "score": row["score"], "reasons": row["reasons"], "risk": row["risk"]})
    with right:
        st.markdown("#### ETF")
        etf_df = st.session_state.results_etf
        if etf_df.empty:
            st.caption("실행 전")
        else:
            for i, row in etf_df.head(5).iterrows():
                result_card({"rank": i + 1, "name": row["name"], "theme": row["theme"], "score": row["score"], "reasons": row["reasons"], "risk": row["risk"]})

elif page == "자동 발굴":
    left, right = st.columns([1.05, 0.95])
    with left:
        st.markdown("### 실행")
        market_mode = st.selectbox("시장 모드", MARKET_MODES)
        term = st.selectbox("기간", TERMS)
        themes = st.multiselect("테마", list(THEME_KEYWORDS.keys()), default=list(THEME_KEYWORDS.keys()))
        run = st.button("종목 발굴 실행", use_container_width=True, type="primary")

    with right:
        st.markdown("### 현재 기준")
        st.markdown(
            """
            - 필수 · 거래대금 / 20일선 / 뉴스 / 테마 / 시총
            - 가점 · 거래대금 강도 / 고점 근접 / 뉴스 강도 / 상대강도
            - 제외 · 최근 급등 / 저유동성 / 20일선 하회
            """
        )
        st.info(MODE_RULES[market_mode])

    if run:
        with st.spinner("국내주식 자동 발굴 중"):
            stock_df = build_stock_candidates()
        with st.spinner("ETF 자동 발굴 중"):
            etf_df = build_etf_candidates()

        if not stock_df.empty:
            stock_df = stock_df[stock_df["theme"].isin(themes)].head(5).copy()
        if not etf_df.empty:
            etf_df = etf_df[etf_df["theme"].isin(themes)].head(5).copy()

        st.session_state.results_stock = stock_df
        st.session_state.results_etf = etf_df
        st.session_state.last_run_msg = datetime.now().strftime("%Y-%m-%d %H:%M 실행 완료")

    if st.session_state.last_run_msg:
        st.caption(st.session_state.last_run_msg)

    st.markdown("### 국내주식 TOP 5")
    if st.session_state.results_stock.empty:
        st.caption("결과 없음")
    else:
        for i, row in st.session_state.results_stock.iterrows():
            result_card({"rank": i + 1, "name": row["name"], "theme": row["theme"], "score": row["score"], "reasons": row["reasons"], "risk": row["risk"]})

    st.markdown("### ETF TOP 5")
    if st.session_state.results_etf.empty:
        st.caption("결과 없음")
    else:
        for i, row in st.session_state.results_etf.iterrows():
            result_card({"rank": i + 1, "name": row["name"], "theme": row["theme"], "score": row["score"], "reasons": row["reasons"], "risk": row["risk"]})

elif page == "조건":
    st.markdown("### 필수 조건")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
            - 국내주식 거래대금 300억 이상
            - 국내주식 시총 2000억 이상
            - 종가 > 20일선
            - 최근 3일 뉴스 존재
            - 핵심 테마 포함
            """
        )
    with c2:
        st.markdown(
            """
            - ETF 거래대금 100억 이상
            - 테마 매칭
            - 수익률 플러스 우대
            - 최근 급등 제외
            - 저유동성 제외
            """
        )

    st.markdown("### 감시 테마")
    st.markdown(" · ".join(THEME_KEYWORDS.keys()))
