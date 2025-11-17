import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="지하철 TOP 10 승하차", layout="centered")

# ---------------------------------------------------
# 📌 100% Streamlit Cloud에서 동작하는 CSV 경로 설정
# ---------------------------------------------------
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT_DIR, "subway.csv")

@st.cache_data
def load_data():
    if not os.path.exists(CSV_PATH):
        st.error(f"❌ CSV 파일을 찾을 수 없습니다.\n경로: {CSV_PATH}")
        st.stop()

    # cp949 → utf-8 순차 시도
    try:
        return pd.read_csv(CSV_PATH, encoding="cp949")
    except:
        return pd.read_csv(CSV_PATH, encoding="utf-8")

df = load_data()
st.success("CSV 로드 성공!")
