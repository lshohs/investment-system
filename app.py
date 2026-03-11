import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(page_title="Morning Radar", page_icon="📈", layout="wide")

st.markdown(
    """
    <style>
    .block-container {max-width: 1160px; padding-top: 1.6rem; padding-bottom: 2rem;}
    .stButton>button {border-radius: 14px; height: 46px; font-weight: 700;}
    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 14px !important;
    }
    .hero {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
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

THEME_BY_NAME = {
    "반도체": ["삼성전자", "SK하이닉스", "한미반도체", "리노공업", "테크윙", "피에스케이", "이수페타시스", "DB하이텍"],
    "AI": ["NAVER", "카카오", "폴라리스오피스", "솔트룩스", "이수페타시스", "한글과컴퓨터"],
    "방산": ["한화에어로스페이스", "LIG넥스원", "현대로템", "한국항공우주", "한화시스템"],
    "원전": ["두산에너빌리티", "한전기술", "비에이치아이", "우리기술", "보성파워텍"],
    "조선": ["HD한국조선해양", "한화오션", "삼성중공업", "HD현대중공업", "HJ중공업"],
    "2차전지": ["에코프로비엠", "에코프로", "포스코퓨처엠", "엘앤에프", "금양", "LG에너지솔루션"],
    "로봇": ["레인보우로보틱스", "두산로보틱스", "로보스타", "유일로보틱스", "티로보틱스"],
    "전력기기": ["HD현대일렉트릭", "LS ELECTRIC", "효성중공업", "제룡전기", "산일전기", "가온전선"],
}

ETF_THEME_RULES = {
    "반도체": ["반도체", "필라델피아"],
    "AI": ["AI", "인공지능", "빅테크", "테크"],
    "방산": ["방산", "디펜스"],
    "원전": ["원전", "원자력", "SMR"],
    "조선": ["조선", "해운"],
    "2차전지": ["2차전지", "배터리", "전기차"],
    "로봇": ["로봇", "자동화"],
    "전력기기": ["전력", "전선", "전력설비", "인프라"],
}

DEFAULT_STOCKS = """종목명,거래대금억,등락률,20일선위,5일상승률,뉴스수,대장주
HD현대일렉트릭,1850,4.8,Y,11,4,Y
한미반도체,1420,3.9,Y,9,3,Y
두산에너빌리티,1180,2.7,Y,8,2,Y
LIG넥스원,920,2.1,Y,7,2,Y
레인보우로보틱스,760,5.4,Y,14,3,Y
에코프로비엠,690,2.2,Y,6,1,N
한화오션,640,3.1,Y,10,2,Y
NAVER,610,1.9,Y,4,2,N"""

DEFAULT_ETFS = """종목명,거래대금억,등락률,20일선위,5일상승률,뉴스수,대장주
TIGER 미국필라델피아반도체,520,2.4,Y,6,1,Y
KODEX AI전력핵심설비,310,1.9,Y,5,1,Y
ACE 미국빅테크TOP7 Plus,280,1.4,Y,4,1,N
KODEX K-방산,250,2.1,Y,5,1,Y
TIGER 원전테마,180,1.8,Y,4,1,Y
TIGER 2차전지TOP10,170,1.2,Y,3,1,N"""

if "stock_results" not in st.session_state:
    st.session_state.stock_results = pd.DataFrame()
if "etf_results" not in st.session_state:
    st.session_state.etf_results = pd.DataFrame()
if "last_run" not in st.session_state:
    st.session_state.last_run = ""


def infer_stock_theme(name: str):
    for theme, names in THEME_BY_NAME.items():
        if any(n in str(name) for n in names):
            return theme
    return None


def infer_etf_theme(name: str):
    text = str(name)
    for theme, keywords in ETF_THEME_RULES.items():
        if any(k.lower() in text.lower() for k in keywords):
            return theme
    return None


def normalize_yes_no(value):
    text = str(value).strip().upper()
    return text in ["Y", "YES", "TRUE", "1", "O"]


def parse_input(text: str, asset_type: str) -> pd.DataFrame:
    if not text.strip():
        return pd.DataFrame()
    try:
        df = pd.read_csv(StringIO(text.strip()))
    except Exception:
        return pd.DataFrame()

    expected = ["종목명", "거래대금억", "등락률", "20일선위", "5일상승률", "뉴스수", "대장주"]
    if not all(col in df.columns for col in expected):
        return pd.DataFrame()

    df = df.copy()
    df["종목명"] = df["종목명"].astype(str).str.strip()
    for col in ["거래대금억", "등락률", "5일상승률", "뉴스수"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["20일선위"] = df["20일선위"].apply(normalize_yes_no)
    df["대장주"] = df["대장주"].apply(normalize_yes_no)
    df["테마"] = df["종목명"].apply(infer_stock_theme if asset_type == "stock" else infer_etf_theme)
    df = df[df["테마"].notna()].copy()
    return df


def score_stock_row(row: pd.Series) -> tuple[int, list[str], str]:
    score = 0
    reasons = []

    if row["거래대금억"] >= 1000:
        score += 25
        reasons.append("거래대금 강함")
    elif row["거래대금억"] >= 500:
        score += 18
        reasons.append("거래대금 양호")
    elif row["거래대금억"] >= 200:
        score += 10
        reasons.append("거래대금 확보")

    if row["20일선위"]:
        score += 20
        reasons.append("20일선 우위")

    if row["등락률"] >= 3:
        score += 15
        reasons.append("상대강도")
    elif row["등락률"] >= 1:
        score += 8

    if row["5일상승률"] >= 30:
        return -1, [], "최근 급등 제외"
    elif row["5일상승률"] >= 12:
        score += 10
        reasons.append("단기 탄력")
    elif row["5일상승률"] >= 3:
        score += 6

    if row["뉴스수"] >= 3:
        score += 10
        reasons.append("뉴스 강도")
    elif row["뉴스수"] >= 1:
        score += 5

    if row["대장주"]:
        score += 15
        reasons.append("테마 대장")

    risk = "단기 과열 확인" if row["5일상승률"] >= 15 else "눌림 유지 확인"
    return int(score), reasons[:4], risk


def score_etf_row(row: pd.Series) -> tuple[int, list[str], str]:
    score = 0
    reasons = []

    if row["거래대금억"] >= 300:
        score += 25
        reasons.append("거래대금 강함")
    elif row["거래대금억"] >= 150:
        score += 18
        reasons.append("거래대금 양호")
    elif row["거래대금억"] >= 70:
        score += 10
        reasons.append("거래대금 확보")

    if row["20일선위"]:
        score += 20
        reasons.append("20일선 우위")

    if row["등락률"] >= 1.5:
        score += 12
        reasons.append("상대강도")
    elif row["등락률"] >= 0.5:
        score += 6

    if row["5일상승률"] >= 25:
        return -1, [], "최근 급등 제외"
    elif row["5일상승률"] >= 5:
        score += 12
        reasons.append("단기 흐름")
    elif row["5일상승률"] > 0:
        score += 6

    if row["대장주"]:
        score += 12
        reasons.append("핵심 ETF")

    risk = "섹터 변동성 확인" if row["5일상승률"] >= 10 else "추세 유지 확인"
    return int(score), reasons[:4], risk


def build_ranked(df: pd.DataFrame, asset_type: str) -> pd.DataFrame:
    rows = []
    if df.empty:
        return pd.DataFrame()
    for _, row in df.iterrows():
        score, reasons, risk = score_stock_row(row) if asset_type == "stock" else score_etf_row(row)
        if score < 0:
            continue
        rows.append({
            "종목명": row["종목명"],
            "테마": row["테마"],
            "점수": score,
            "이유": reasons if reasons else ["기본 통과"],
            "주의": risk,
            "거래대금억": row["거래대금억"],
        })
    if not rows:
        return pd.DataFrame()
    out = pd.DataFrame(rows).sort_values(["점수", "거래대금억"], ascending=[False, False]).reset_index(drop=True)
    return out.head(5)


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


st.sidebar.title("Morning Radar")
page = st.sidebar.radio("", ["대시보드", "발굴 실행", "가이드"], label_visibility="collapsed")

st.markdown(
    """
    <div class='hero'>
        <div style='font-size:0.92rem;opacity:0.82'>오전 발굴기 · 국내주식 / 국내상장 ETF</div>
        <div style='font-size:2rem;font-weight:800;margin-top:6px'>Morning Radar</div>
        <div style='margin-top:10px;opacity:0.9'>거래대금 상위 입력 → 자동 TOP 5</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if page == "대시보드":
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("시장", "국내주식 · ETF")
    with c2:
        st.metric("후보", "TOP 5")
    with c3:
        st.metric("테마", "8")

    left, right = st.columns(2)
    with left:
        st.markdown("### 국내주식")
        if st.session_state.stock_results.empty:
            st.caption("실행 전")
        else:
            for i, row in st.session_state.stock_results.iterrows():
                result_card(i + 1, row["종목명"], row["테마"], int(row["점수"]), row["이유"], row["주의"])
    with right:
        st.markdown("### ETF")
        if st.session_state.etf_results.empty:
            st.caption("실행 전")
        else:
            for i, row in st.session_state.etf_results.iterrows():
                result_card(i + 1, row["종목명"], row["테마"], int(row["점수"]), row["이유"], row["주의"])

elif page == "발굴 실행":
    left, right = st.columns(2)
    with left:
        st.markdown("### 국내주식 입력")
        stock_text = st.text_area("", value=DEFAULT_STOCKS, height=260, label_visibility="collapsed")
    with right:
        st.markdown("### ETF 입력")
        etf_text = st.text_area(" ", value=DEFAULT_ETFS, height=260, label_visibility="collapsed")

    run = st.button("종목 발굴 실행", use_container_width=True, type="primary")

    if run:
        stock_df = parse_input(stock_text, "stock")
        etf_df = parse_input(etf_text, "etf")
        st.session_state.stock_results = build_ranked(stock_df, "stock")
        st.session_state.etf_results = build_ranked(etf_df, "etf")
        st.session_state.last_run = "실행 완료"

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 국내주식 TOP 5")
        if st.session_state.stock_results.empty:
            st.caption("결과 없음")
        else:
            for i, row in st.session_state.stock_results.iterrows():
                result_card(i + 1, row["종목명"], row["테마"], int(row["점수"]), row["이유"], row["주의"])
    with c2:
        st.markdown("### ETF TOP 5")
        if st.session_state.etf_results.empty:
            st.caption("결과 없음")
        else:
            for i, row in st.session_state.etf_results.iterrows():
                result_card(i + 1, row["종목명"], row["테마"], int(row["점수"]), row["이유"], row["주의"])

elif page == "가이드":
    st.markdown("### 입력 형식")
    st.code("종목명,거래대금억,등락률,20일선위,5일상승률,뉴스수,대장주")
    st.markdown("### 예")
    st.code(DEFAULT_STOCKS)
    st.markdown("### 기준")
    st.markdown("- 거래대금 강도")
    st.markdown("- 20일선 우위")
    st.markdown("- 5일 상승률 과열 제외")
    st.markdown("- 뉴스수 보조 가점")
    st.markdown("- 대장주 가점")
