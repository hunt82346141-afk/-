# pages/app.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="지하철 TOP 10 승하차", layout="centered")

st.title("📊 지하철 역 TOP 10 (승차+하차 합계 기준)")
st.markdown("날짜와 호선을 선택하면 TOP 10 역을 Plotly 그래프로 보여줍니다.")

# ---------------------------------------------------
# CSV 파일 로드 (Streamlit Cloud에서 절대 경로 문제 방지)
# ---------------------------------------------------
CSV_PATH = "subway.csv"   # ⬅ 이것만 써야 Cloud에서 100% 동작

@st.cache_data
def load_data():
    try:
        return pd.read_csv(CSV_PATH, encoding="cp949")
    except:
        return pd.read_csv(CSV_PATH, encoding="utf-8")

df = load_data()
