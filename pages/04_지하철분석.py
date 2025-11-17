# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime

st.set_page_config(page_title="지하철 상위 역 비교", layout="centered")

st.title("📊 지하철 역 TOP 10 (승차+하차 기준) — Plotly 인터랙티브")
st.markdown(
    "날짜와 호선을 선택하면 해당 조건에서 **승차수 + 하차수 합계**가 가장 큰 10개 역을 막대그래프로 보여줍니다."
)

# ---------- 데이터 로드 함수 ----------
@st.cache_data(show_spinner=False)
def load_data(path_candidates=None):
    """
    path_candidates: list of file paths to try in order.
    파일 인코딩 문제(특히 한국어 csv)는 cp949로 먼저 시도하고 실패하면 utf-8로 재시도합니다.
    """
    candidates = path_candidates or [
        "/mnt/data/subway mukusipda.csv",
        "subway mukusipda.csv",
        "/workspace/subway mukusipda.csv",
        "./subway mukusipda.csv",
    ]

    for p in candidates:
        try:
            df = pd.read_csv(p, encoding="cp949")
            st.info(f"데이터를 로드했습니다: {p}")
            return df
        except Exception as e_cp:
            try:
                df = pd.read_csv(p, encoding="utf-8")
                st.info(f"데이터를 로드했습니다 (utf-8): {p}")
                return df
            except Exception:
                continue

    # 파일 업로더 대안
    uploaded = st.file_uploader("CSV 파일을 업로드하세요 (또는 저장소에 'subway mukusipda.csv'가 있어야 합니다)", type=["csv"])
    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded, encoding="cp949")
            return df
        except Exception:
            uploaded.seek(0)
            df = pd.read_csv(uploaded, encoding="utf-8")
            return df

    st.warning("데이터 파일을 찾지 못했습니다. 좌측의 파일 업로더로 csv를 업로드하거나 저장소에 'subway mukusipda.csv' 파일을 업로드해주세요.")
    return None

df = load_data()

if df is None:
    st.stop()

# ---------- 전처리 ----------
# 컬럼명 표준화: 공백이나 불일치에 대비
df = df.rename(columns=lambda x: x.strip())
required_cols = ["사용일자", "노선명", "역명", "승차총승객수", "하차총승객수"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"필수 컬럼이 없습니다: {missing}. CSV 컬럼명을 확인해주세요.")
    st.write("현재 컬럼들:", list(df.columns))
    st.stop()

# 날짜형 변환
def parse_date_col(s):
    # 사용일자가 YYYYMMDD 또는 숫자형으로 왔다고 가정
    try:
        return pd.to_datetime(s.astype(str), format="%Y%m%d")
    except Exception:
        return pd.to_datetime(s, errors="coerce")

df["사용일자"] = parse_date_col(df["사용일자"])

# 숫자형 변환
for c in ["승차총승객수", "하차총승객수"]:
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)

# 합계 컬럼
df["승하합계"] = df["승차총승객수"] + df["하차총승객수"]

# ---------- UI: 날짜 / 호선 선택 ----------
st.sidebar.header("필터")
# 사용 가능한 날짜와 호선 목록
available_dates = sorted(df["사용일자"].dropna().dt.date.unique())
available_lines = sorted(df["노선명"].dropna().unique())

# 기본값: 2025년 내의 날짜 중 하나가 있으면 그 중 하나 선택
default_date = None
# 우선, 2025년(예: 2025-01-01 ~ 2025-12-31) 중 하나가 있으면 default로 사용
for d in available_dates:
    if d.year == 2025:
        default_date = d
        break
if default_date is None and available_dates:
    default_date = available_dates[0]

selected_date = st.sidebar.date_input("날짜 선택 (YYYY-MM-DD)", value=default_date, min_value=min(available_dates) if available_dates else None, max_value=max(available_dates) if available_dates else None)
selected_line = st.sidebar.selectbox("호선 선택", options=["전체"] + available_lines, index=0)

st.sidebar.markdown("---")
st.sidebar.markdown("⚙️ CSV 인코딩 문제가 있을 경우 `cp949` 또는 `utf-8`로 읽어옵니다.")

# ---------- 데이터 필터링 ----------
# 날짜 필터는 시간정보를 제외한 날짜 비교
filtered = df[df["사용일자"].dt.date == selected_date]

if selected_line != "전체":
    filtered = filtered[filtered["노선명"] == selected_line]

if filtered.empty:
    st.warning("조건에 해당하는 데이터가 없습니다. 다른 날짜/호선을 선택해주세요.")
    st.stop()

# TOP 10 역 (승하합계 기준)
topn = filtered.sort_values("승하합계", ascending=False).head(10).copy()
topn = topn.reset_index(drop=True)

# ---------- 색상 생성: 1등 빨강, 나머지 파란색 그라데이션 ----------
def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*[max(0,min(255,int(v))) for v in rgb])

def interpolate_color(c1, c2, t):
    return tuple(c1[i] + (c2[i] - c1[i]) * t for i in range(3))

# 첫 색상: 빨강
first_color = "#ff0000"
# 파란색 시작(진한), 파란색 끝(연한)
blue_dark = "#0d6efd"   # 진한 파랑
blue_light = "#cfe2ff"  # 연한 파랑

colors = []
n = len(topn)
if n > 0:
    colors.append(first_color)
for i in range(1, n):
    t = (i - 1) / max(1, n - 2) if n > 2 else 0.5
    c = interpolate_color(hex_to_rgb(blue_dark), hex_to_rgb(blue_light), t)
    colors.append(rgb_to_hex(c))

# ---------- Plotly 막대 그래프 ----------
bars = go.Bar(
    x=topn["역명"],
    y=topn["승하합계"],
    marker=dict(color=colors),
    text=[f"승차: {a:,d}<br>하차: {b:,d}<br>합계: {c:,d}" for a,b,c in zip(topn["승차총승객수"], topn["하차총승객수"], topn["승하합계"])],
    hoverinfo="text",
)

layout = go.Layout(
    title=f"{selected_date} — {selected_line} 조건 상위 10개 역 (승차+하차 합계)",
    xaxis=dict(title="역명"),
    yaxis=dict(title="승객수 (합계)"),
    margin=dict(l=40, r=20, t=80, b=120),
    hovermode="closest",
)

fig = go.Figure(data=[bars], layout=layout)

# x축 레이블이 길 경우 회전
fig.update_layout(xaxis_tickangle=-45)

st.plotly_chart(fig, use_container_width=True)

# ---------- 하단: 데이터테이블 ----------
with st.expander("🔎 상위 10개 역 데이터 보기"):
    display_df = topn[["사용일자", "노선명", "역명", "승차총승객수", "하차총승객수", "승하합계"]].copy()
    display_df["사용일자"] = display_df["사용일자"].dt.strftime("%Y-%m-%d")
    st.dataframe(display_df.style.format({ "승차총승객수":"{:,}", "하차총승객수":"{:,}", "승하합계":"{:,}"}), height=320)

st.markdown("---")
st.caption("제작: Streamlit + Plotly | CSV 인코딩 문제시 cp949 또는 utf-8로 재시도합니다.")
