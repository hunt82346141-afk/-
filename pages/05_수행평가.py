# 파일: pages/analysis_app.py
# CSV 파일: 루트 폴더에 '수행평가.csv'

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="범죄별 지역 Top10 분석", layout="wide")

# 데이터 불러오기
def load_data(path):
    try:
        return pd.read_csv(path)
    except:
        return pd.read_csv(path, encoding='cp949')

# Top10 계산
def get_top10(df, crime_col, region_col, crime):
    subset = df[df[crime_col] == crime]
    counts = subset[region_col].fillna('알수없음').value_counts().head(10)
    return counts.reset_index().rename(columns={'index': region_col, region_col: 'count'})

# 색상
def bar_colors(n):
    base = px.colors.sequential.Plasma
    if n == 1:
        return ['#FF0000']
    idx = np.linspace(0, len(base)-1, n-1).astype(int)
    colors = ['#FF0000'] + [base[i] for i in idx]
    return colors

# UI 시작
st.title("범죄 클릭하면 지역 Top10 바로 보여주는 앱 🔎🔥")

# CSV 입력
with st.sidebar:
    st.header("파일 설정")
    path = st.text_input("CSV 파일 경로", value="수행평가.csv")
    uploaded = st.file_uploader("또는 CSV 업로드", type=['csv'])
    if uploaded:
        df = pd.read_csv(uploaded)
    else:
        df = load_data(path)

st.success(f"데이터 로드 완료! 총 {len(df):,}행")

cols = df.columns.tolist()

with st.sidebar:
    st.header("컬럼 선택")
    crime_col = st.selectbox("범죄 컬럼(범죄명만 있어야 함)", cols)
    region_col = st.selectbox("지역 컬럼(지역명만 있어야 함)", cols)

# 범죄 목록
df[crime_col] = df[crime_col].astype(str)
crime_list = sorted(df[crime_col].unique())

selected = st.selectbox("보고 싶은 범죄를 선택하세요", crime_list)

# Top10 계산
result = get_top10(df, crime_col, region_col, selected)

st.subheader(f"'{selected}'이 가장 많이 발생한 지역 TOP 10 🏆")

# 그래프
theme_colors = bar_colors(len(result))
fig = px.bar(result, x=region_col, y='count', text='count')
fig.data[0].marker.color = theme_colors
fig.update_traces(textposition='outside')
fig.update_layout(template='plotly_white', xaxis_title='지역', yaxis_title='건수')

st.plotly_chart(fig, use_container_width=True)

# 테이블 보기
with st.expander("데이터 표로 보기"):
    st.dataframe(result)

st.markdown("---")
st.info("범죄 클릭 → 지역 Top10 자동 정렬! 필요하면 추가 기능도 만들어줄게 😊")

"""
# requirements.txt
streamlit
pandas
plotly
numpy
"""
