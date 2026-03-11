import streamlit as st

st.set_page_config(page_title="개인 투자 시스템", page_icon="📈", layout="wide")

GUIDES = {
    "시장 브리핑 보는 기준": {
        "category": "시장 판단",
        "summary": "시장의 큰 흐름을 먼저 보고 종목 판단으로 들어갑니다.",
        "purpose": "감정적인 매매보다 시장 환경을 먼저 점검하기 위한 기준입니다.",
        "points": [
            "코스피·코스닥 지수의 20일선 위치 확인",
            "전일 미국 증시 흐름과 반도체/빅테크 방향 체크",
            "환율·금리·외국인 수급 동시 점검",
            "상승장·중립장·방어장 중 어디인지 분류",
        ],
        "checklist": [
            "오늘 시장이 정상 모드인지 방어 모드인지 구분했는가?",
            "지수보다 강한 업종이 어디인지 확인했는가?",
            "전일 뉴스와 오늘 수급이 같은 방향인지 확인했는가?",
        ],
        "caution": "시장 방향이 애매하면 종목 확신이 있어도 비중을 줄입니다.",
        "one_line": "시장부터 보고 종목은 그다음에 본다.",
    },
    "종목 발굴 TOP10 기준": {
        "category": "종목 발굴",
        "summary": "매매 후보 종목을 고를 때 사용하는 핵심 스크리닝 기준입니다.",
        "purpose": "막연한 종목 선택을 줄이고 반복 가능한 기준을 만들기 위함입니다.",
        "points": [
            "최근 거래대금 증가 종목",
            "강한 테마 대장주 또는 2등주",
            "20일선 위 추세 유지",
            "외국인 또는 기관 수급 유입",
            "최근 뉴스 또는 정책 모멘텀",
            "전고점 돌파 시도",
            "동일 업종 동반 상승",
            "ETF 흐름과 연동",
            "실적 모멘텀 존재",
            "차트 구조가 깨지지 않은 종목",
        ],
        "checklist": [
            "거래대금이 충분한가?",
            "테마 흐름이 살아있는가?",
            "대장주가 이미 크게 올라 부담되지 않는가?",
        ],
        "caution": "뉴스만 있고 거래대금이 없는 종목은 후보에서 제외합니다.",
        "one_line": "거래대금·테마·추세 세 가지가 맞는 종목만 본다.",
    },
    "국내주식 스윙 매매 지침": {
        "category": "스윙 매매",
        "summary": "단기 파동을 활용한 스윙 매매 기본 원칙입니다.",
        "purpose": "감정적인 추격매수를 줄이고 구조적인 매매를 하기 위함입니다.",
        "points": [
            "추세 상승 종목 중심으로 접근",
            "20일선 지지 또는 돌파 구간 매수",
            "분할매수 원칙 유지",
            "손절 기준 사전 설정",
            "테마 지속 여부 매일 확인",
        ],
        "checklist": [
            "추세가 살아있는 종목인가?",
            "테마가 유지되고 있는가?",
            "손절가를 정했는가?",
        ],
        "caution": "급등 후 눌림 없는 종목은 추격 매수하지 않습니다.",
        "one_line": "스윙은 추세 속 눌림에서 시작한다.",
    },
    "ETF 전용 매매 지침": {
        "category": "ETF",
        "summary": "ETF 매매 시 적용하는 기본 전략입니다.",
        "purpose": "개별주보다 안정적으로 운용하면서 기준 없는 매매를 막기 위함입니다.",
        "points": [
            "지수 방향과 동일한 ETF 선택",
            "20일선 위 추세 확인",
            "분할매수 원칙 유지",
            "거래대금 충분한 ETF 우선",
            "레버리지 상품은 비중 제한",
        ],
        "checklist": [
            "기초지수를 이해했는가?",
            "ETF 목적이 명확한가?",
            "손절 기준을 정했는가?",
        ],
        "caution": "유동성이 낮은 ETF는 피합니다.",
        "one_line": "ETF는 지수 방향과 함께 간다.",
    },
    "배당형 ETF 관리 기준": {
        "category": "ETF",
        "summary": "배당 ETF 운용 시 현금흐름 중심으로 관리합니다.",
        "purpose": "가격 변동보다 배당 흐름을 안정적으로 확보하기 위함입니다.",
        "points": [
            "월배당 ETF 중심 관리",
            "배당수익률과 변동성 함께 확인",
            "과도한 하락 시 비중 조절",
            "배당 지급 일정 체크",
        ],
        "checklist": [
            "배당 안정성이 유지되는가?",
            "기초자산 구조를 이해했는가?",
            "배당 목적 계좌에 맞는가?",
        ],
        "caution": "고배당만 보고 매수하면 가격 하락 리스크가 있습니다.",
        "one_line": "배당 ETF는 현금흐름 중심으로 본다.",
    },
    "ISA 계좌 운용 원칙": {
        "category": "계좌 운영",
        "summary": "절세 계좌의 특성을 활용한 투자 원칙입니다.",
        "purpose": "세금 효율을 높이기 위해 계좌 목적에 맞게 운용합니다.",
        "points": [
            "배당형 ETF 중심 운용",
            "과도한 단타 매매 지양",
            "연간 수익 구조 관리",
            "만기 이전 전략 점검",
        ],
        "checklist": [
            "세금 구조를 이해했는가?",
            "배당 흐름이 안정적인가?",
            "계좌 목적과 맞는 종목인가?",
        ],
        "caution": "단기 매매 계좌로 사용하면 절세 효과가 줄어듭니다.",
        "one_line": "ISA는 절세 중심 계좌로 운용한다.",
    },
    "연금계좌 운용 원칙": {
        "category": "계좌 운영",
        "summary": "장기 투자 중심의 연금 계좌 전략입니다.",
        "purpose": "퇴직 이후 안정적인 자산 흐름을 만들기 위함입니다.",
        "points": [
            "장기 성장 ETF 중심",
            "분산 투자 유지",
            "시장 급락 시 추가 매수",
            "장기 보유 원칙",
        ],
        "checklist": [
            "장기 투자 가능한 자산인가?",
            "변동성을 감당할 수 있는가?",
            "연금 목적과 맞는가?",
        ],
        "caution": "단기 매매를 반복하면 계좌 목적이 흔들립니다.",
        "one_line": "연금계좌는 장기 복리 전략으로 운용한다.",
    },
    "장 시작 전 체크리스트": {
        "category": "체크리스트",
        "summary": "장 시작 전에 반드시 확인해야 할 항목입니다.",
        "purpose": "감정 매매를 줄이고 준비된 상태로 시장을 맞이하기 위함입니다.",
        "points": [
            "미국 증시 흐름 확인",
            "환율과 금리 확인",
            "강한 테마 파악",
            "관심 종목 정리",
        ],
        "checklist": [
            "오늘 시장 분위기를 파악했는가?",
            "매매 후보 종목을 정했는가?",
            "리스크 상황을 점검했는가?",
        ],
        "caution": "준비 없이 장을 시작하면 추격 매매 확률이 높아집니다.",
        "one_line": "장 시작 전 준비가 하루 매매를 결정한다.",
    },
    "장 마감 후 복기 체크리스트": {
        "category": "체크리스트",
        "summary": "매매 후 반드시 기록하고 점검해야 할 항목입니다.",
        "purpose": "반복되는 실수를 줄이고 매매 실력을 개선하기 위함입니다.",
        "points": [
            "오늘 매매 종목 기록",
            "매매 이유와 결과 분석",
            "손절과 익절 판단 검토",
            "시장 흐름 재확인",
        ],
        "checklist": [
            "계획된 매매였는가?",
            "감정 매매가 있었는가?",
            "다음에 개선할 점은 무엇인가?",
        ],
        "caution": "복기 없는 매매는 같은 실수를 반복하게 됩니다.",
        "one_line": "매매는 끝나도 복기는 반드시 한다.",
    },
}

SOURCE_OPTIONS = [
    "킴스미국주식",
    "킴스 주식",
    "김정란의 머니부띠끄",
    "기릿의 주식노트",
    "박곰희TV",
    "이효석 아카데미",
    "기타 유튜브",
    "커뮤니티",
]

SAMPLE_IDEAS = [
    {
        "stock": "한미반도체",
        "theme": "반도체",
        "sources": ["기릿의 주식노트", "김정란의 머니부띠끄", "커뮤니티"],
        "memo": "반도체 장비, 테마 강도 유지, 반복 언급",
        "turnover": True,
        "theme_up": True,
        "leader": True,
        "trend": True,
        "news": True,
    },
    {
        "stock": "HD현대일렉트릭",
        "theme": "전력기기",
        "sources": ["이효석 아카데미", "박곰희TV"],
        "memo": "전력 인프라 수요와 AI 전력 확대 관련 언급",
        "turnover": True,
        "theme_up": True,
        "leader": True,
        "trend": True,
        "news": False,
    },
    {
        "stock": "두산에너빌리티",
        "theme": "원전/전력",
        "sources": ["킴스 주식", "커뮤니티"],
        "memo": "테마 확장성과 관심도는 높으나 타이밍 확인 필요",
        "turnover": True,
        "theme_up": True,
        "leader": True,
        "trend": False,
        "news": True,
    },
]

MARKET_MODES = {
    "정상 모드": {
        "condition": "지수 20일선 위, 거래대금 증가, 강한 테마 존재",
        "strategy": "최대 3종목, 비중 100% 가능",
    },
    "중립 모드": {
        "condition": "지수 20일선 근처, 테마 순환 빠름",
        "strategy": "최대 2종목, 비중 50~70%",
    },
    "방어 모드": {
        "condition": "지수 20일선 아래, 외국인 매도 우세, 하락 종목 다수",
        "strategy": "최대 1종목, 현금 70% 유지",
    },
}

DISCOVERY_ITEMS = GUIDES["종목 발굴 TOP10 기준"]["points"]


def render_guide(title: str) -> None:
    guide = GUIDES[title]
    st.subheader(title)
    st.caption(f"{guide['category']} · {guide['summary']}")
    st.write(f"**목적**  \n{guide['purpose']}")

    st.write("**핵심 규칙**")
    for item in guide["points"]:
        st.markdown(f"- {item}")

    st.write("**체크리스트**")
    for item in guide["checklist"]:
        st.markdown(f"- {item}")

    st.warning(guide["caution"])
    st.info(guide["one_line"])


def calc_idea_score(selected_sources: list[str]) -> int:
    youtube_count = len([s for s in selected_sources if s != "커뮤니티"])
    community = 1 if "커뮤니티" in selected_sources else 0
    if youtube_count >= 2:
        return 4 + community
    if youtube_count == 1:
        return 2 + community
    return community


def calc_total_score(idea_score: int, market_score: int) -> int:
    return idea_score + market_score


def decision_text(score: int) -> str:
    if score >= 10:
        return "최상급 기회"
    if score >= 9:
        return "적극 검토"
    if score >= 8:
        return "관심 종목"
    if score >= 7:
        return "후보 종목"
    return "관찰"


def evaluate_sample(item: dict) -> tuple[int, int, int, str]:
    idea = calc_idea_score(item["sources"])
    market = sum([
        item["turnover"],
        item["theme_up"],
        item["leader"],
        item["trend"],
        item["news"],
    ])
    total = idea + market
    return idea, market, total, decision_text(total)


st.title("개인 투자 시스템")
st.caption("유튜브·커뮤니티 아이디어 → 증권사 MTS 확인 → 네이버 증권 보조 확인 흐름으로 만든 Streamlit 버전")

menu = st.sidebar.radio(
    "메뉴",
    [
        "홈",
        "오늘의 시장",
        "관심 종목",
        "아이디어 소스",
        "종목 발굴",
        "매매 전략",
        "계좌 운영",
        "하루 루틴",
        "설정",
    ],
)

if menu == "홈":
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.subheader("시장 모드")
        mode = st.selectbox("오늘의 시장 상태", list(MARKET_MODES.keys()))
        st.success(f"{mode} · {MARKET_MODES[mode]['strategy']}")
        st.write(f"**판단 기준**: {MARKET_MODES[mode]['condition']}")

        st.subheader("핵심 원칙")
        for rule in [
            "시장 먼저 본다",
            "유튜브는 아이디어, MTS는 확인",
            "거래대금과 대장주를 우선 확인한다",
            "손절 기준을 먼저 정한다",
            "장 마감 후 반드시 복기한다",
        ]:
            st.markdown(f"- {rule}")

    with col2:
        st.subheader("계좌 운영 한눈에 보기")
        st.info("일반계좌 : 스윙 및 기동성 중심")
        st.info("ISA : 절세 + 배당형 ETF 중심")
        st.info("연금 : 장기 성장 ETF 중심")

    st.subheader("오늘의 관심 종목 후보")
    for item in SAMPLE_IDEAS:
        idea, market, total, decision = evaluate_sample(item)
        with st.container(border=True):
            st.write(f"**{item['stock']}** · {item['theme']}")
            st.write(f"출처: {' · '.join(item['sources'])}")
            st.write(f"메모: {item['memo']}")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("아이디어", idea)
            c2.metric("시장", market)
            c3.metric("총점", total)
            c4.metric("판정", decision)

elif menu == "오늘의 시장":
    st.subheader("시장 모드 판단")
    cols = st.columns(3)
    for idx, (name, data) in enumerate(MARKET_MODES.items()):
        with cols[idx]:
            with st.container(border=True):
                st.write(f"**{name}**")
                st.write(data["condition"])
                st.success(data["strategy"])

    st.divider()
    guide_title = st.selectbox("지침 선택", list(GUIDES.keys()), index=0)
    render_guide(guide_title)

elif menu == "관심 종목":
    st.subheader("중복 언급 종목")
    sorted_ideas = sorted(SAMPLE_IDEAS, key=lambda x: len(x["sources"]), reverse=True)
    for item in sorted_ideas:
        st.write(f"- {item['stock']} : 언급 {len(item['sources'])}회")

    st.divider()
    st.subheader("관심 종목 자동 점수 예시")
    for item in SAMPLE_IDEAS:
        idea, market, total, decision = evaluate_sample(item)
        with st.expander(f"{item['stock']} · 총점 {total} · {decision}"):
            st.write(f"테마: {item['theme']}")
            st.write(f"출처: {' · '.join(item['sources'])}")
            st.write(f"선정 이유: {item['memo']}")
            st.write(f"아이디어 점수: {idea}")
            st.write(f"시장 점수: {market}")

elif menu == "아이디어 소스":
    st.subheader("커뮤니티·유튜브 아이디어 기록")
    stock = st.text_input("종목명")
    theme = st.text_input("관련 테마")
    sources = st.multiselect("출처 선택", SOURCE_OPTIONS)
    memo = st.text_area("왜 관심이 갔는지 메모", height=120)

    idea_score = calc_idea_score(sources)
    col1, col2, col3 = st.columns(3)
    col1.metric("입력 종목", stock if stock else "미입력")
    col2.metric("아이디어 점수", idea_score)
    col3.metric("판단", "반복 언급" if idea_score >= 4 else "1차 아이디어" if idea_score >= 2 else "관찰")

    st.write("**점수 기준**")
    st.markdown("- 유튜브 1곳 언급 → +2")
    st.markdown("- 유튜브 2곳 이상 언급 → +4")
    st.markdown("- 커뮤니티 언급 → +1")
    st.info("커뮤니티와 유튜브는 아이디어를 주고, 거래대금과 차트는 최종 판단을 준다.")

elif menu == "종목 발굴":
    st.subheader("종목 발굴 점수표")
    st.caption("주 확인 경로: 증권사 MTS / 보조 확인 경로: 네이버 증권")
    candidate = st.text_input("종목명을 입력하세요")

    selected_items = []
    cols = st.columns(2)
    for i, item in enumerate(DISCOVERY_ITEMS):
        with cols[i % 2]:
            checked = st.checkbox(item, key=f"disc_{i}")
            if checked:
                selected_items.append(item)

    discovery_score = len(selected_items)
    st.metric("TOP10 기준 점수", f"{discovery_score}/10")
    if candidate:
        st.write(f"**{candidate}** 평가 결과: {discovery_score}/10")

    st.divider()
    st.subheader("아이디어 + 시장 점수 통합 판정")
    sources_for_score = st.multiselect("아이디어 출처", SOURCE_OPTIONS, key="score_sources")
    idea_score = calc_idea_score(sources_for_score)

    market_checks = {
        "거래대금 증가": st.checkbox("거래대금 증가", key="m1"),
        "테마 전체 상승": st.checkbox("테마 전체 상승", key="m2"),
        "대장주 또는 2등주": st.checkbox("대장주 또는 2등주", key="m3"),
        "20일선 위 추세": st.checkbox("20일선 위 추세", key="m4"),
        "뉴스 재료 확인": st.checkbox("뉴스 재료 확인", key="m5"),
    }
    market_score = sum(market_checks.values())
    total_score = calc_total_score(idea_score, market_score)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("아이디어 점수", idea_score)
    c2.metric("시장 점수", market_score)
    c3.metric("총점", total_score)
    c4.metric("최종 판단", decision_text(total_score))

    st.info("8점 이상은 매매 후보, 7점은 후보 관찰, 6점 이하는 보수적으로 봅니다.")
    render_guide("종목 발굴 TOP10 기준")

elif menu == "매매 전략":
    st.subheader("매매 판단 순서")
    st.markdown("- 1. 유튜브·커뮤니티에서 아이디어 발견")
    st.markdown("- 2. MTS에서 거래대금·차트·수급 확인")
    st.markdown("- 3. 네이버 증권에서 뉴스·테마 확장 확인")
    st.markdown("- 4. 점수 8 이상만 매매 후보 등록")
    st.divider()
    for title in ["국내주식 스윙 매매 지침", "ETF 전용 매매 지침", "배당형 ETF 관리 기준"]:
        render_guide(title)
        st.divider()

elif menu == "계좌 운영":
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("일반계좌")
        st.write("목적: 스윙 매매")
        st.write("대상: 국내주식, 테마주")
        st.write("특징: 기동성 우선")
    with c2:
        st.subheader("ISA")
        st.write("목적: 절세 + 배당")
        st.write("대상: 배당형 ETF, 커버드콜 ETF")
        st.write("특징: 과도한 단타 지양")
    with c3:
        st.subheader("연금계좌")
        st.write("목적: 장기 복리")
        st.write("대상: 미국지수 ETF, 성장 ETF")
        st.write("특징: 장기 보유 중심")

    st.divider()
    render_guide("ISA 계좌 운용 원칙")
    st.divider()
    render_guide("연금계좌 운용 원칙")

elif menu == "하루 루틴":
    st.subheader("장 시작 전 체크")
    morning_items = [
        "미국 증시 확인",
        "환율 확인",
        "금리 확인",
        "강한 테마 확인",
        "관심 종목 3개 선정",
    ]
    for item in morning_items:
        st.checkbox(item, key=f"morning_{item}")

    st.divider()
    st.subheader("장 마감 후 복기")
    st.text_input("오늘 매매 종목")
    st.text_area("매매 이유", height=100)
    st.text_area("잘한 점", height=80)
    st.text_area("개선할 점", height=80)

    st.divider()
    render_guide("장 시작 전 체크리스트")
    st.divider()
    render_guide("장 마감 후 복기 체크리스트")

elif menu == "설정":
    st.subheader("기본 설정값")
    st.markdown("- 정상 모드: 최대 3종목, 비중 100% 가능")
    st.markdown("- 중립 모드: 최대 2종목, 비중 50~70%")
    st.markdown("- 방어 모드: 최대 1종목, 현금 70% 유지")
    st.markdown("- 매매 후보 기준: 총점 8 이상")
    st.markdown("- 주 확인 경로: 증권사 MTS")
    st.markdown("- 보조 확인 경로: 네이버 증권")

    st.divider()
    st.subheader("출처별 성격 정리")
    st.markdown("- 킴스미국주식 / 킴스 주식: 미국시장, ETF, 기술주 아이디어")
    st.markdown("- 김정란의 머니부띠끄 / 기릿의 주식노트: 국내 종목 아이디어")
    st.markdown("- 박곰희TV / 이효석 아카데미: 시장 방향, 거시 흐름, 섹터 힌트")
    st.markdown("- 커뮤니티: 관심도 보조 확인")

st.sidebar.divider()
st.sidebar.caption("현숙님 개인 투자 운영 시스템 · Streamlit 초안")
