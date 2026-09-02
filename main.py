import random
import pandas as pd
import streamlit as st

st.set_page_config(page_title="다중 종목 주식 시뮬레이션", layout="wide")
st.title("🏛️ 다중 종목 포트폴리오 투자 시뮬레이션")

# 1. 초기 종목 데이터 및 기업별 뉴스 데이터베이스
STOCKS = {
    "삼성전자": {
        "price": 70_000,
        "news": [
            {
                "text": "🚀 반도체 신기술 개발 성공으로 수요 폭발 예상",
                "min": 0.08,
                "max": 0.15,
            },
            {
                "text": "📉 글로벌 스마트폰 판매량 감소로 실적 먹구름",
                "min": -0.10,
                "max": -0.03,
            },
        ],
    },
    "현대차": {
        "price": 200_000,
        "news": [
            {
                "text": "⚡ 전기차 신모델 북미 판매량 역대 최고 기록",
                "min": 0.06,
                "max": 0.12,
            },
            {
                "text": "⚠️ 노조 파업 가능성으로 생산 차질 우려",
                "min": -0.08,
                "max": -0.02,
            },
        ],
    },
    "카카오": {
        "price": 50_000,
        "news": [
            {
                "text": "✨ 신규 AI 서비스 라이브 개시 및 유저 급증",
                "min": 0.07,
                "max": 0.18,
            },
            {
                "text": "📢 공정위 규제 강화 발표로 플랫폼 사업 위축",
                "min": -0.12,
                "max": -0.04,
            },
        ],
    },
}

COMMON_NEWS = [
    {
        "text": "☕ 시장 전체에 큰 변동 없는 평이한 하루",
        "min": -0.02,
        "max": 0.02,
    },
    {
        "text": "🏦 기준 금리 인하 발표! 증시 전체 호재",
        "min": 0.03,
        "max": 0.08,
    },
    {
        "text": "📉 경기 침체 공포로 증시 전반 하락세",
        "min": -0.07,
        "max": -0.02,
    },
]

# 2. 세션 상태 초기화
if "cash" not in st.session_state:
  st.session_state.cash = 20_000_000  # 2천만 원
  st.session_state.portfolio = {name: 0 for name in STOCKS}  # 보유 수량
  st.session_state.prices = {
      name: data["price"] for name, data in STOCKS.items()
  }  # 현재가
  st.session_state.day = 1
  st.session_state.price_history = {
      name: [data["price"]] for name, data in STOCKS.items()
  }
  st.session_state.news_history = []

# 3. 사이드바: 자산 주문 창
st.sidebar.header("💼 내 계좌 및 거래")
st.sidebar.write(f"**현재 날짜:** Day {st.session_state.day}")
st.sidebar.write(f"**보유 현금:** {st.session_state.cash:,} 원")

st.sidebar.markdown("---")
selected_stock = st.sidebar.selectbox("거래할 종목 선택", list(STOCKS.keys()))

curr_price = st.session_state.prices[selected_stock]
curr_shares = st.session_state.portfolio[selected_stock]

st.sidebar.write(f"**{selected_stock} 현재가:** {curr_price:,} 원")
st.sidebar.write(f"**보유 수량:** {curr_shares} 주")

# 매수 / 매도
max_buy = st.session_state.cash // curr_price
buy_qty = st.sidebar.number_input(
    "매수 수량", min_value=0, max_value=max_buy, value=0, key="buy"
)
if st.sidebar.button("매수", use_container_width=True):
  if buy_qty > 0:
    st.session_state.cash -= buy_qty * curr_price
    st.session_state.portfolio[selected_stock] += buy_qty
    st.sidebar.success(f"{selected_stock} {buy_qty}주 매수 완료!")
    st.rerun()

sell_qty = st.sidebar.number_input(
    "매도 수량", min_value=0, max_value=curr_shares, value=0, key="sell"
)
if st.sidebar.button("매도", use_container_width=True):
  if sell_qty > 0:
    st.session_state.cash += sell_qty * curr_price
    st.session_state.portfolio[selected_stock] -= sell_qty
    st.sidebar.success(f"{selected_stock} {sell_qty}주 매도 완료!")
    st.rerun()

# 4. 메인 화면
col1, col2 = st.columns([2, 1])

with col1:
  # 턴 진행
  if st.button("▶️ 다음 날로 넘어가기 (턴 진행)", use_container_width=True):
    st.session_state.day += 1

    # 종목별 변동성 적용
    for name in STOCKS:
      # 40% 확률로 개별 종목 특화 뉴스, 60% 확률로 공통 뉴스
      if random.random() < 0.4:
        news_item = random.choice(STOCKS[name]["news"])
        news_text = f"[{name}] {news_item['text']}"
      else:
        news_item = random.choice(COMMON_NEWS)
        news_text = f"[전체] {news_item['text']}"

      rate = random.uniform(news_item["min"], news_item["max"])
      new_price = max(1000, int(st.session_state.prices[name] * (1 + rate)))

      st.session_state.prices[name] = new_price
      st.session_state.price_history[name].append(new_price)

      # 최근 뉴스에 저장
      st.session_state.news_history.insert(
          0, f"Day {st.session_state.day} - {news_text} ({rate*100:+.1f}%)"
      )

    st.rerun()

  # 총 자산 계산
  stock_eval = sum(
      st.session_state.portfolio[name] * st.session_state.prices[name]
      for name in STOCKS
  )
  total_assets = st.session_state.cash + stock_eval
  profit = total_assets - 20_000_000
  profit_rate = (profit / 20_000_000) * 100

  st.metric(
      label="내 총 평가 자산",
      value=f"{total_assets:,} 원",
      delta=f"{profit:,} 원 ({profit_rate:+.2f}%)",
  )

  # 종목별 가격 차트
  st.subheader("📈 종목별 주가 추이")
  chart_df = pd.DataFrame(st.session_state.price_history)
  st.line_chart(chart_df)

with col2:
  # 자산 비중 요약
  st.subheader("📊 자산 구성")
  asset_data = {"현금": st.session_state.cash}
  for name in STOCKS:
    eval_val = (
        st.session_state.portfolio[name] * st.session_state.prices[name]
    )
    if eval_val > 0:
      asset_data[name] = eval_val

  asset_df = pd.DataFrame(
      list(asset_data.items()), columns=["자산", "평가금액"]
  )
  st.dataframe(asset_df, hide_index=True, use_container_width=True)

  # 뉴스 로그
  st.subheader("📜 발생 뉴스 기록")
  for news in st.session_state.news_history[:8]:
    st.caption(news)
