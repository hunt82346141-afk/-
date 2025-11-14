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

# Tabs: Country view + MBTI leaderboard
tab1, tab2 = st.tabs(["국가별 보기", "MBTI 상위국가(Top10)"])

####################
# Tab 1: Country View
####################
with tab1:
    st.sidebar.header("Controls")
    country = st.sidebar.selectbox("국가 선택", options=df['Country'].tolist())
    show_table = st.sidebar.checkbox("표 표시", value=False)

    # Filter row for selected country
    row = df[df['Country'] == country]
    if row.empty:
        st.error("선택한 국가 데이터가 없습니다.")
    else:
        row = row.iloc[0]

        # Prepare data for plotting
        values = [float(row[c]) for c in mbti_cols]
        labels = mbti_cols

        plot_df = pd.DataFrame({'MBTI': labels, 'Value': values})
        plot_df = plot_df.sort_values('Value', ascending=False).reset_index(drop=True)

        # Color logic for tab1: 1st red, others blue gradient
        def make_color_list_tab1(n):
            colors = []
            for i in range(n):
                if i == 0:
                    colors.append('rgba(220,20,60,1)')  # red for 1st
                else:
                    t = (i-1) / max(1, n-2)
                    r = int(0 + t*(200-0))
                    g = int(70 + t*(160))
                    b = int(200 + t*(55))
                    alpha = 1 - 0.5 * t
                    colors.append(f'rgba({r},{g},{b},{alpha:.2f})')
            return colors

        colors = make_color_list_tab1(len(plot_df))

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

        top_value = plot_df.loc[0, 'Value']
        fig.add_annotation(x=0, y=top_value, text='1위', showarrow=False, yshift=20,
                           font=dict(color='rgb(220,20,60)', size=12))

        if show_table:
            st.subheader(f"{country} 데이터 테이블")
            st.dataframe(plot_df)

        st.plotly_chart(fig, use_container_width=True)

####################
# Tab 2: MBTI Leaderboard
####################
with tab2:
    st.header("MBTI 유형별 Top 국가(상위 10개)")
    mbti_choice = st.selectbox("MBTI 유형 선택", options=mbti_cols)

    # prepare df: Country + selected MBTI
    df_leader = df[['Country', mbti_choice]].copy()
    # ensure numeric
    df_leader[mbti_choice] = pd.to_numeric(df_leader[mbti_choice], errors='coerce').fillna(0)
    df_leader_sorted = df_leader.sort_values(by=mbti_choice, ascending=False).reset_index(drop=True)

    top_n = 10
    top_df = df_leader_sorted.head(top_n).copy()

    # Try to find Korea-like entries (allow 'Korea', '대한민국', 'South Korea', 'Republic of Korea')
    korea_mask = df['Country'].astype(str).str.contains('korea', case=False, na=False) | \
                 df['Country'].astype(str).str.contains('대한민국', case=False, na=False) | \
                 df['Country'].astype(str).str.contains('south korea', case=False, na=False) | \
                 df['Country'].astype(str).str.contains('republic of korea', case=False, na=False)
    korea_rows = df[korea_mask]

    korea_present = False
    korea_row = None
    if not korea_rows.empty:
        korea_row = korea_rows.iloc[0]
        korea_val = float(korea_row[mbti_choice]) if pd.notna(korea_row[mbti_choice]) else 0.0
        # check if Korea already in top_df
        if korea_row['Country'] in top_df['Country'].values:
            korea_present = True
        else:
            # append Korea to the list (so user always sees Korea highlighted)
            append_row = pd.DataFrame([[korea_row['Country'], korea_val]], columns=['Country', mbti_choice])
            top_df = pd.concat([top_df, append_row], ignore_index=True)

    # Build colors: Korea -> red; others -> blue gradient based on rank (excluding Korea)
    n_bars = len(top_df)
    colors = []
    # create gradient list for non-korea bars
    def blue_gradient(k):
        # interpolates 0..1 to blue shades
        t = k / max(1, max(1, n_bars-1))
        r = int(0 + t*(200-0))
        g = int(70 + t*(160))
        b = int(200 + t*(55))
        alpha = 1 - 0.5 * t
        return f'rgba({r},{g},{b},{alpha:.2f})'

    for idx, r in top_df.iterrows():
        name = r['Country']
        if korea_row is not None and name == korea_row['Country']:
            colors.append('rgba(220,20,60,1)')
        else:
            colors.append(blue_gradient(idx))

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=top_df['Country'],
        y=top_df[mbti_choice],
        marker_color=colors,
        text=top_df[mbti_choice].apply(lambda v: f"{v:.4f}"),
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>비율: %{y:.4f}<extra></extra>'
    ))

    fig2.update_layout(
        title=f"Top {top_n} countries by {mbti_choice}",
        xaxis_title='Country',
        yaxis_title='비율',
        template='plotly_white',
        height=560,
    )

    # If Korea was appended but not in original top10, show info
    if korea_row is not None and (not korea_present) and (korea_row['Country'] not in df_leader_sorted.head(top_n)['Country'].values):
        st.info(f"참고: 선택한 MBTI에 대해 한국('{korea_row['Country']}')은 상위 {top_n}에 들지 않아 목록 하단에 추가되었습니다.")

    st.plotly_chart(fig2, use_container_width=True)

    # Optional table
    if st.checkbox('표 보기 (Top 리스트)', value=False):
        st.dataframe(top_df.reset_index(drop=True))

# Small notes and tips
st.markdown("---")
st.markdown("**사용 팁**: 
- CSV는 `Country` 컬럼과 16개의 MBTI 컬럼(예: INFJ, ISFJ, INTP, ... ESFJ)을 포함해야 합니다.
- 탭1: 국가 선택 시 해당 국가 MBTI 분포를 표시합니다.
- 탭2: MBTI를 선택하면 해당 유형의 상위 국가(Top10)를 표시하고, 한국은 빨간색으로 강조됩니다. (한국 데이터가 존재하면 항상 강조 표시됩니다.)")

# Provide raw download of the dataframe
@st.cache_data
def df_to_csv(df_in):
    return df_in.to_csv(index=False).encode('utf-8')

csv_bytes = df_to_csv(df)
st.download_button('전체 데이터 다운로드 (CSV)', data=csv_bytes, file_name=f"mbti_full_dataset.csv", mime='text/csv')

# End of app
