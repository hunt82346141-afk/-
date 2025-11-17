import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import os

st.set_page_config(page_title="지하철 TOP 10 승하차", layout="centered")

st.title("📊 지하철 상위 역 분석 (Plotly 인터랙티브)")

# -----------------------------------
# 1) CSV 파일을 레포에서 자동 로드
# -----------------------------------
CSV_PATH = "data/subway.csv"   # ← 레포에 반드시 이 경로로 넣기

@st.cache_data
def load_data():
    if not os.path.exists(CSV_PATH):
        st.error(f"❌ 데이터 파일을 찾을 수 없습니다.\n\n레포에 `{CSV_PATH}` 경로로 CSV를 넣어주세요.")
        st.stop()

    # cp949 → utf8 순서로 시도
    try:
        return pd.read_csv(CSV_PATH, encoding="cp949")
    except:
        return pd.read_csv(CSV_PATH, encoding="utf-8")

df = load_data()

# -----------------------------------
# 2) 데이터 전처리
# -----------------------------------
df = df.rename(columns=lambda x: x.strip())

df["사용일자"] = pd.to_datetime(df["사용일자"].astype(str), format="%Y%m%d")
df["승차총승객수"] = pd.to_numeric(df["승차총승객수"], errors="coerce").fillna(0)
df["하차총승객수"] = pd.to_numeric(df["하차총승객수"], errors="coerce").fillna(0)
df["승하합계"] = df["승차총승객수"] + df["하차총승객수"]

# -----------------------------------
# 3) UI - 날짜 & 호선 선택
# -----------------------------------
available_dates = sorted(df["사용일자"].dt.date.unique())
available_lines = sorted(df["노선명"].unique())

selected_date = st.sidebar.date_input("날짜 선택", value=available_dates[0])
selected_line = st.sidebar.selectbox("호선 선택", options=available_lines)

# -----------------------------------
# 4) 필터링 및 TOP 10 계산
# -----------------------------------
filtered = df[
    (df["사용일자"].dt.date == selected_date) &
    (df["노선명"] == selected_line)
]

if filtered.empty:
    st.warning("해당 조건의 데이터가 없습니다.")
    st.stop()

top10 = filtered.sort_values("승하합계", ascending=False).head(10)

# -----------------------------------
# 5) 색상 설정 (1등=빨강, 나머지=파랑 → 연파랑 그라데이션)
# -----------------------------------
colors = ["#ff0000"] + [
    f"rgba(0, 102, 255, {1 - i*0.08})"
    for i in range(1, len(top10))
]

# -----------------------------------
# 6) Plotly 그래프
# -----------------------------------
fig = go.Figure()
fig.add_trace(go.Bar(
    x=top10["역명"],
    y=top10["승하합계"],
    marker=dict(color=colors),
    text=top10["승하합계"],
    hovertemplate="역명: %{x}<br>합계: %{y:,}"
))
fig.update_layout(
    title=f"{selected_date} — {selected_line} 승하차 합계 TOP 10",
    xaxis_title="역명",
    yaxis_title="승차+하차 합계",
    xaxis_tickangle=-45,
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------------
# 7) 데이터 테이블
# -----------------------------------
st.dataframe(top10)
