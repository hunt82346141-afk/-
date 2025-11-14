# Streamlit MBTI Visualizer (Clean Version)
# Requirements: streamlit, pandas, plotly

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="MBTI Country Visualizer", layout="wide")

st.title("🌍 MBTI Country Visualizer — Interactive Plotly")
st.write("국가별 MBTI 데이터를 업로드하면 인터랙티브한 그래프로 시각화해줍니다.")

# Upload
uploaded = st.file_uploader("CSV 업로드 (Country + 16 MBTI columns)", type=["csv"])
if uploaded is None:
    st.warning("CSV 파일을 업로드하세요.")
    st.stop()

df = pd.read_csv(uploaded)
if 'Country' not in df.columns:
    st.error("CSV에 'Country' 컬럼이 없습니다.")
    st.stop()

# MBTI Columns
mbti_cols = [c for c in df.columns if c != 'Country']

# Select country
country = st.selectbox("국가 선택", df['Country'].unique())
row = df[df['Country'] == country].iloc[0]

# Prepare
values = [float(row[c]) for c in mbti_cols]
plot_df = pd.DataFrame({'MBTI': mbti_cols, 'Value': values}).sort_values('Value', ascending=False)

# Color gradient
colors = []
for i in range(len(plot_df)):
    if i == 0:
        colors.append('rgba(220,20,60,1)')  # red
    else:
        t = i / (len(plot_df)-1)
        r = int(0 + t*200)
        g = int(70 + t*160)
        b = int(200 + t*55)
        alpha = 1 - 0.4 * t
        colors.append(f"rgba({r},{g},{b},{alpha:.2f})")

# Plotly chart
fig = go.Figure()
fig.add_trace(go.Bar(
    x=plot_df['MBTI'], y=plot_df['Value'], marker_color=colors,
    text=plot_df['Value'].round(4), textposition='auto'
))
fig.update_layout(title=f"{country} MBTI 비율", template='plotly_white', height=500)

st.plotly_chart(fig, use_container_width=True)
