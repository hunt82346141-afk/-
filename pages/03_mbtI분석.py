# streamlit_mbti_app.py
# Streamlit app: country별 MBTI 비율을 Plotly로 인터랙티브하게 시각화

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="MBTI by Country — Interactive", layout="wide")

st.title("🌍 Country MBTI Visualizer — Plotly + Streamlit")
st.markdown("Upload a CSV that has a `Country` column and 16 MBTI columns (INFJ, ISFJ, INTP, ... ESFJ).")

@st.cache_data
def load_csv(uploaded_file):
    return pd.read_csv(uploaded_file)

# File uploader
uploaded = st.file_uploader("CSV 파일 업로드 (Country + 16 MBTI columns)", type=["csv"])

if uploaded is None:
    st.warning("먼저 CSV 파일을 업로드하세요. 예시 파일이 없으면 상단의 'Upload' 버튼으로 파일을 넣어주세요.")
    st.stop()

# Load dataframe
df = load_csv(uploaded)

# Basic validation
if 'Country' not in df.columns:
    st.error("CSV에 'Country' 컬럼이 없습니다. 파일을 확인해주세요.")
    st.stop()

# Identify MBTI columns automatically (exclude Country)
mbti_cols = [c for c in df.columns if c.lower() != 'country']
if len(mbti_cols) != 16:
    st.warning(f"경고: 감지된 MBTI 컬럼 수 = {len(mbti_cols)} (예상 16). 자동으로 사용 가능한 컬럼을 선택합니다.")

# Sidebar controls
st.sidebar.header("Controls")
country = st.sidebar.selectbox("국가 선택", options=df['Country'].tolist())
show_table = st.sidebar.checkbox("표 표시", value=False)

# Filter row for selected country
row = df[df['Country'] == country]
if row.empty:
    st.error("선택한 국가 데이터가 없습니다.")
    st.stop()

row = row.iloc[0]

# Prepare data for plotting
values = [float(row[c]) for c in mbti_cols]
labels = mbti_cols

# Create a dataframe sorted by value (descending) but keep original order for x axis labeling if desired
plot_df = pd.DataFrame({'MBTI': labels, 'Value': values})
plot_df = plot_df.sort_values('Value', ascending=False).reset_index(drop=True)

# Color logic:
# 1st (rank 1) -> pure red
# others -> blue gradient from deep blue to pale blue based on rank

def make_color_list(n):
    colors = []
    for i in range(n):
        if i == 0:
            colors.append('rgba(220,20,60,1)')  # crimson-like red for 1st
        else:
            # create gradient for blue: interpolate between rgb(0,70,200) and rgb(200,230,255)
            t = (i-1) / max(1, n-2)  # 0..1 across ranks 2..n
            r = int(0 + t*(200-0))
            g = int(70 + t*(160))
            b = int(200 + t*(55))
            # slightly reduce opacity for lower-ranked bars for a faded look
            alpha = 1 - 0.5 * t
            colors.append(f'rgba({r},{g},{b},{alpha:.2f})')
    return colors

colors = make_color_list(len(plot_df))

# Build Plotly bar chart
fig = go.Figure()
fig.add_trace(go.Bar(
    x=plot_df['MBTI'],
    y=plot_df['Value'],
    marker_color=colors,
    text=plot_df['Value'].apply(lambda v: f"{v:.3f}"),
    textposition='auto',
    hovertemplate='<b>%{x}</b><br>비율: %{y:.4f}<extra></extra>'
))

fig.update_layout(
    title=f"{country} — MBTI 비율 (내림차순)",
    xaxis_title='MBTI 유형',
    yaxis_title='비율',
    template='plotly_white',
    bargap=0.2,
    height=520,
)

# Add annotation to top bar
top_label = plot_df.loc[0, 'MBTI']
top_value = plot_df.loc[0, 'Value']
fig.add_annotation(x=0, y=top_value, text='1위', showarrow=False, yshift=20,
                   font=dict(color='rgb(220,20,60)', size=12))

# Show table option
if show_table:
    st.subheader(f"{country} 데이터 테이블")
    st.dataframe(plot_df)

# Display chart
st.plotly_chart(fig, use_container_width=True)

# Small notes and tips
st.markdown("---")
st.markdown("**사용 팁**: \n- CSV는 `Country` 컬럼과 16개의 MBTI 컬럼(예: INFJ, ISFJ, INTP, ... ESFJ)을 포함해야 합니다.\n- 색상 규칙: 1등은 빨강, 2등부터는 파란 계열의 그라데이션으로 표시됩니다.")

# Provide raw download of the filtered row as CSV
@st.cache_data
def row_to_csv(r):
    return r.to_frame().T.to_csv(index=False).encode('utf-8')

csv_bytes = row_to_csv(row[ ['Country'] + mbti_cols ])
st.download_button('선택 국가 데이터 다운로드 (CSV)', data=csv_bytes, file_name=f"{country}_mbti.csv", mime='text/csv')


# End of app
