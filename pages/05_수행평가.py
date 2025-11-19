# 파일: pages/analysis_app.py
# 위치: Streamlit 앱의 pages 폴더 아래에 넣어주세요.
# CSV 파일: 루트 폴더(앱 루트)에 '수행평가.csv' 파일을 넣어주세요.
# requirements.txt 내용은 파일 하단에 포함되어 있습니다.

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="수행평가 데이터 분석 📊", layout="wide")

# -------------------------
# 유틸 함수
# -------------------------

def load_data(path):
    # 인코딩 시도: utf-8 -> cp949 순서
    try:
        df = pd.read_csv(path)
    except Exception:
        try:
            df = pd.read_csv(path, encoding='cp949')
        except Exception as e:
            st.error(f"파일을 불러오는 데 실패했어요: {e}")
            return None
    return df


def top_locations_for_crime(df, crime_col, location_col, crime_value, topn=10):
    sub = df[df[crime_col] == crime_value]
    counts = sub[location_col].fillna('알수없음').value_counts().nlargest(topn)
    return counts.reset_index().rename(columns={'index': location_col, location_col: 'count'})


def make_bar_colors(n):
    # 첫 번째는 빨간색, 나머지는 그라데이션(파랑계열)으로 채워줌
    base = px.colors.sequential.Plasma
    # base 길이와 n-1 맞추기
    if n <= 1:
        return ['#FF0000']
    # sample gradient from base
    colors = []
    colors.append('#FF0000')
    # pick n-1 from base evenly
    idxs = np.linspace(0, len(base)-1, n-1).astype(int)
    for i in idxs:
        colors.append(base[i])
    return colors


# -------------------------
# 앱 UI
# -------------------------

st.title("수행평가 데이터 분석 🎯")
st.markdown("안녕! 데이터 분석 도와줄게 — 친절하고 센스있게 📈✨\n좌측 사이드바에서 설정을 골라줘~")

with st.sidebar:
    st.header("설정 🛠️")
    csv_path = st.text_input("CSV 파일 경로", value='수행평가.csv')
    uploaded = st.file_uploader("파일 업로드 (선택) - 루트의 CSV 대신 업로드하려면 여기로", type=['csv'])
    if uploaded is not None:
        csv_path = uploaded
    st.caption("파일을 업로드하지 않으면 루트 폴더의 '수행평가.csv'를 시도합니다.")

# 데이터 로드
if csv_path is None:
    st.stop()

if isinstance(csv_path, str):
    df = load_data(csv_path)
else:
    # uploaded file object
    try:
        df = pd.read_csv(csv_path)
    except Exception:
        df = pd.read_csv(csv_path, encoding='cp949')

if df is None:
    st.stop()

st.success(f"데이터 불러오기 성공! 레코드 수: {len(df):,}개 🎉")

# 컬럼 선택 - 자동 추천
cols = list(df.columns)
st.subheader("데이터 컬럼 미리보기 🔍")
st.write(cols)

# 기본 후보 이름들
crime_candidates = [c for c in cols if any(x in c.lower() for x in ['범죄','죄','type','crime','incident','사건','죄명'])]
location_candidates = [c for c in cols if any(x in c.lower() for x in ['장소','위치','주소','발생지','location','place','area','site'])]
date_candidates = [c for c in cols if any(x in c.lower() for x in ['일자','날짜','date','발생일','time','시간'])]

st.sidebar.subheader("컬럼 매핑 🗺️")
crime_col = st.sidebar.selectbox("범죄(또는 사건) 컬럼을 골라줘", options=['선택안함']+cols, index=0)
location_col = st.sidebar.selectbox("장소(또는 발생지) 컬럼을 골라줘", options=['선택안함']+cols, index=0)
date_col = st.sidebar.selectbox("날짜(선택) 컬럼", options=['선택안함']+cols, index=0)

# 자동 추천 버튼
if st.sidebar.button('추천 컬럼 자동선택 🤖'):
    if crime_candidates:
        crime_col = crime_candidates[0]
    if location_candidates:
        location_col = location_candidates[0]
    if date_candidates:
        date_col = date_candidates[0]
    st.experimental_rerun()

# 기본 통계
st.header("기본 탐색 🌱")
with st.expander("데이터 샘플 보기 (상위 10개)"):
    st.dataframe(df.head(10))

with st.expander("결측치 / 타입 요약"):
    na_counts = df.isna().sum()
    types = df.dtypes
    info = pd.DataFrame({'missing': na_counts, 'dtype': types})
    st.dataframe(info)

# 범죄 컬럼이 선택되지 않으면 멈춤 안내
if crime_col == '선택안함' or location_col == '선택안함':
    st.info("범죄 컬럼과 장소 컬럼을 사이드바에서 꼭 선택해줘~ 그래야 분석할 수 있어요 😊")
    st.stop()

# 준비: 범죄 종류 선택
unique_crimes = df[crime_col].fillna('알수없음').unique()
unique_crimes = [str(x) for x in unique_crimes]
unique_crimes_sorted = sorted(unique_crimes, key=lambda x: (str(x)))
selected_crime = st.selectbox("어떤 범죄(사건)를 볼래?", options=unique_crimes_sorted)

# Top N 설정
top_n = st.slider("Top N 장소 개수", min_value=3, max_value=20, value=10)

# 집계
counts_df = top_locations_for_crime(df, crime_col, location_col, selected_crime, topn=top_n)

st.subheader(f"'{selected_crime}'이(가) 발생한 장소 Top {top_n} 🏆")
st.write("가장 많이 발생한 장소부터 정렬했어 — 클릭으로 더 자세히 볼 수 있어요!")

# 차트 그리기: 첫 번째는 빨강, 나머지는 그라데이션
colors = make_bar_colors(len(counts_df))
fig = px.bar(counts_df, x=location_col, y='count', text='count')
# plotly에서 개별 색 설정
for i, d in enumerate(fig.data):
    # fig.data는 1개의 바 trace이기 때문에 색을 따로 주기 위해 marker.color를 리스트로 바꿈
    fig.data[0].marker.color = colors

fig.update_layout(yaxis_title='발생 건수', xaxis_title='장소', bargap=0.2, template='plotly_white')
fig.update_traces(texttemplate='%{text}', textposition='outside')
fig.update_xaxes(tickangle= -45)

st.plotly_chart(fig, use_container_width=True)

# 상세 테이블
with st.expander("상세 테이블 보기📋"):
    st.dataframe(counts_df)

# 시간 흐름 분석 (있다면)
if date_col != '선택안함':
    st.header('시간 흐름 분석 ⏱️')
    tmp = df[[date_col, crime_col]].copy()
    # 날짜 파싱 시도
    try:
        tmp['__dt'] = pd.to_datetime(tmp[date_col], errors='coerce')
        timeline = tmp[tmp[crime_col]==selected_crime].dropna(subset=['__dt'])
        if len(timeline) > 0:
            timeline['year_month'] = timeline['__dt'].dt.to_period('M').astype(str)
            trend = timeline['year_month'].value_counts().sort_index().reset_index()
            trend.columns = ['year_month', 'count']
            fig2 = px.line(trend, x='year_month', y='count', markers=True)
            fig2.update_layout(xaxis_title='연-월', yaxis_title='건수')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info('선택한 날짜 컬럼에서 유효한 날짜를 찾지 못했어. 다른 컬럼을 골라보거나 날짜 포맷을 확인해줘.')
    except Exception as e:
        st.warning(f'시간 흐름 분석 중 오류가 났어: {e}')

# 다운로드 버튼
with st.expander('결과 다운로드 ⤵️'):
    csv_result = counts_df.to_csv(index=False)
    st.download_button('Top 장소 CSV로 다운받기', data=csv_result, file_name=f'top_{selected_crime}_locations.csv', mime='text/csv')

# 친절한 마무리
st.markdown('---')
st.markdown('필요하면 컬럼 자동 매핑을 도와주거나, 시각화 옵션을 더 추가해줄게! 😎')


# -------------------------
# 아래는 프로젝트에 포함할 requirements.txt 내용
# -------------------------

"""
# 파일: requirements.txt
streamlit
pandas
plotly
numpy
"""
