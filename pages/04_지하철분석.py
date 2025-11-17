# pages/app.py
import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import os

st.set_page_config(page_title="지하철 TOP 10 승하차", layout="centered")

st.title("📊 지하철 역 TOP 10 (승차+하차 합계 기준)")
st.markdown("날짜와 호선을 선택하면 TOP 10 역을 Plotly 그래프로 보여줍니다.")

# ---------------------------------------------------
# 1) CSV 파일 로드 (항상 repo 루트의 subway.csv 읽기)
# ---------------------------------------------------
CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "subway.csv")

@st.cache_data
def load_data():
    if not os.path.exists(CSV_PATH):
        st.error(f"❌ 데이터 파일 subway.csv 를 찾을 수 없습니다.\n\n현재 경로: {CSV_PATH}")
        st.stop()

    try:
        return pd.read_csv(CSV_PATH, encoding="cp949")
    except:
        return pd.read_csv(CSV_PATH, encoding="utf-8")

df = load_data()

# ---------------------------------------------------
# 2) 전처리
# ---------------------------------------------------
df = df.rename(columns=lambda x: x.strip())

df["사용일자"] = pd.to_datetime(df["사용일자"].astype(str), format="%Y%m%d")
df["승차총승객수"] = pd.to_numeric(df["승차총승객수"], errors="coerce").fillna(0)
df["하차총승객수"] = pd.to_numeric(df["하차총승객수"], errors="coerce").fillna(0)
df["승하합계"] = df["승차총승객수"] + df["하차총승객수"]

# ---------------------------------------------------
# 3) UI - 날짜 & 호선 선택
# ---------------------------------------------------
available_dates = sorted(df["사용일자"].dt.date.unique())
available_lines = sorted(df["노선명"].unique())

selected_date = st.sidebar.date_input("📅 날짜 선택", value=available_dates[0])
selected_line = st.sidebar.selectbox("🚇 호선 선택", available_lines)

# ---------------------------------------------------
# 4) 필터링
# ---------------------------------------------------
filtered = df[
    (df["사용일자"].dt.date == selected_date) &
    (df["노선명"] == selected_line)
]

if filtered.empty:
    st.warning("해당 조건의 데이터가 없습니다. 다른 날짜/호선을 선택해주세요.")
    st.stop()

# TOP 10
top10 = filtered.sort_values("승하합계", ascending=False).head(10).reset_index(drop=True)

# ---------------------------------------------------
# 5) 색상: 1등 빨강, 나머지 파랑 → 연파랑 그라데이션
# ---------------------------------------------------
colors = ["#ff0000"]
for i in range(1, len(top10)):
    alpha = 1 - (i * 0.08)
    colors.append(f"rgba(0, 102, 255, {alpha})")

# ---------------------------------------------------
# 6) Plotly 막대 그래프
# ---------------------------------------------------
fig = go.Figure()
fig.add_trace(go.Bar(
    x=top10["역명"],
    y=top10["승하합계"],
    marker=dict(color=colors),
    text=[f"{v:,}" for v in top10["승하합계"]],
    hovertemplate="역명: %{x}<br>승하 합계: %{y:,}명"
))

fig.update_layout(
    title=f"{selected_date} — {selected_line} 승하차 합계 TOP 10",
    xaxis_title="역명",
    yaxis_title="승하차 합계",
    xaxis_tickangle=-40,
    margin=dict(l=40, r=20, t=60, b=100)
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# 7) 테이블
# ---------------------------------------------------
st.subheader("📄 데이터 테이블")
st.dataframe(top10)
