import random
import streamlit as st

st.set_page_config(page_title="경제 뉴스 기반 주식 게임", layout="wide")
st.title("📰 뉴스 대치형 주식 투자 시뮬레이션")

# 1. 경제 뉴스 데이터베이스 (뉴스 내용, 최소 변동률, 최대 변동률)
NEWS_DATABASE = [
    {"news": "🚀 해당 기업, 혁신 신제품 발표로 대박 조짐!", "min": 0.08, "max": 0.18},
    {"news": "📈 분기 실적 발표, 시장 예상치 대폭 상회!", "min": 0.05, "max": 0.12},
    {"news": "🤝 글로벌 대기업과 대규모 공급 계약 체결", "min": 0.04, "max": 0.10},
    {"news": "☕ 평이한 하루, 특이 악재나 호재 없음", "min": -0.02, "max": 0.02},
    {"news": "📉 원자재 가격 상승으로 영업이익 감소 우려", "min": -0.08, "max": -0.03},
    {"news": "⚠️ 주요 제품에서 결함 발견, 리콜 진행 중", "min": -0.15, "max": -0.05},
    {"news": "💥 CEO의 개인적 스캔들로 주가 불확실성 증대", "min": -0.12, "max": -0.04},
]

# 2. 세션 상태 초기화
if "cash" not in st.session_state:
    st.session_state.cash = 10_000_000  # 1천만 원
    st.session_state.shares = 0
    st.session_state.price = 50_000
    st.session_state.day = 1
    st.session_state.price_history = [50_000]
    st.session_state.current_news = "게임이 시작되었습니다. 첫 턴을 진행해보세요!"
    st.session_state.news_history = []

# 3. 사이드바: 보유 현황 & 거래 기능
st.sidebar.header("💼 내 계좌 현황")
st.sidebar.write(f"**현재 날짜:** Day {st.session_state.day}")
st.sidebar.write(f"**보유 현금:** {st.session_state.cash:,} 원")
st.sidebar.write(f"**보유 주식:** {st.session_state.shares} 주")
st.sidebar.write(f"**현재 주가:** {st.session_state.price:,} 원")

st.sidebar.markdown("---")
st.sidebar.header("🛒 매매 주문")

# 매수 로직
max_buy = st.session_state.cash // st.session_state.price
buy_qty = st.sidebar.number_input("매수 수량", min_value=0, max_value=max_buy, value=0, key="buy_qty")
if st.sidebar.button("매수", use_container_width=True):
    if buy_qty > 0:
        cost = buy_qty * st.session_state.price
        st.session_state.cash -= cost
        st.session_state.shares += buy_qty
        st.sidebar.success(f"{buy_qty}주 매수 완료!")
        st.rerun()

# 매도 로직
sell_qty = st.sidebar.number_input("매도 수량", min_value=0, max_value=st.session_state.shares, value=0, key="sell_qty")
if st.sidebar.button("매도", use_container_width=True):
    if sell_qty > 0:
        income = sell_qty * st.session_state.price
        st.session_state.cash += income
        st.session_state.shares -= sell_qty
        st.sidebar.success(f"{sell_qty}주 매도 완료!")
        st.rerun()

# 4. 메인 화면 구성
col1, col2 = st.columns([2, 1])

with col1:
    # 턴 진행 버튼 및 자산 요약
    if st.button("▶️ 다음 날로 넘어가기 (턴 종료)", use_container_width=True):
        st.session_state.day += 1
        
        # 뉴스 뽑기 및 주가 반영
        selected_news = random.choice(NEWS_DATABASE)
        rate = random.uniform(selected_news["min"], selected_news["max"])
        
        # 주가 업데이트
        new_price = max(1000, int(st.session_state.price * (1 + rate))) # 최소 1,000원 보장
        st.session_state.price = new_price
        st.session_state.price_history.append(new_price)
        
        # 뉴스 메시지 구성 및 이력 저장
        change_pct = rate * 100
        news_text = f"[Day {st.session_state.day}] {selected_news['news']} ({change_pct:+.1f}%)"
        st.session_state.current_news = news_text
        st.session_state.news_history.insert(0, news_text)
        st.rerun()

    # 자산 지표
    total_assets = st.session_state.cash + (st.session_state.shares * st.session_state.price)
    profit = total_assets - 10_000_000
    profit_rate = (profit / 10_000_000) * 100

    st.metric(
        label="총 평가 자산",
        value=f"{total_assets:,} 원",
        delta=f"{profit:,} 원 ({profit_rate:+.2f}%)"
    )

    # 최근 뉴스 헤드라인 강조
    st.info(f"📢 **오늘의 뉴스:** {st.session_state.current_news}")

    # 주가 차트
    st.subheader("📊 주가 변동 추이")
    st.line_chart(st.session_state.price_history)

with col2:
    # 지난 뉴스 타임라인 보기
    st.subheader("📜 지난 뉴스 기록")
    if st.session_state.news_history:
        for news_item in st.session_state.news_history[:10]: # 최근 10개만 출력
            st.caption(news_item)
    else:
        st.write("아직 발생한 뉴스가 없습니다.")
