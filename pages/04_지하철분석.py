# pages/app.py
import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import os
import traceback

st.set_page_config(page_title="지하철 TOP 10 (디버그 친화적)", layout="centered")
st.title("지하철 TOP10 (승차+하차) — 디버그 친화적 버전")
st.markdown("이 앱은 CSV를 repo 루트의 `subway.csv`에서 읽습니다. 문제가 생기면 아래 디버그 정보를 확인하세요.")

# ------------------------------
# CSV 경로: repo root의 subway.csv
# ------------------------------
ROOT = os.path.dirname(os.path.dirname(__file__))  # pages -> repo root
CSV_CANDIDATES = [
    os.path.join(ROOT, "subway.csv"),
    os.path.join(ROOT, "data", "subway.csv"),
    os.path.join(ROOT, "subway_mukusipda.csv"),
    os.path.join(ROOT, "data", "subway_mukusipda.csv"),
]

st.sidebar.header("디버그 옵션")
show_debug = st.sidebar.checkbox("상세 디버그 로그 표시", value=True)
st.sidebar.markdown("CSV 경로 후보:\n" + "\n".join(CSV_CANDIDATES))

@st.cache_data
def try_load_csv(paths):
    last_exc = None
    for p in paths:
        if not os.path.exists(p):
            continue
        try:
            # try cp949 then utf-8 then pandas default
            try:
                df = pd.read_csv(p, encoding="cp949")
                return df, p, None
            except Exception as e1:
                try:
                    df = pd.read_csv(p, encoding="utf-8")
                    return df, p, None
                except Exception as e2:
                    # try with default (let pandas infer)
                    df = pd.read_csv(p)
                    return df, p, None
        except Exception as e:
            last_exc = e
            continue
    return None, None, last_exc

df, used_path, load_exc = try_load_csv(CSV_CANDIDATES)

if df is None:
    st.error("CSV 파일을 찾지 못했거나 로드에 실패했습니다.")
    if load_exc is not None:
        st.exception(load_exc)
    st.info("다음 위치들 중 하나에 파일을 두세요 (repo 루트 권장):")
    for p in CSV_CANDIDATES:
        st.write(f"- {p}")
    st.stop()

# Show file info
try:
    fsize = os.path.getsize(used_path)
    st.sidebar.write("로드된 파일:", used_path)
    st.sidebar.write(f"파일 크기: {fsize:,} bytes")
except Exception:
    pass

# ------------------------------
# 컬럼 정리 및 자동 매핑
# ------------------------------
orig_cols = list(df.columns)
st.sidebar.write("원본 컬럼 (샘플):", orig_cols[:10])

# Normalize names for matching
def norm(s):
    return "".join(s.split()).lower()

normalized = {norm(c): c for c in orig_cols}

# expected keys (normalized)
expected = {
    "date": ["사용일자", "date", "일자", "날짜"],
    "line": ["노선명", "line", "호선"],
    "station": ["역명", "역", "station", "stationname"],
    "ons": ["승차총승객수", "승차", "ons", "승차수"],
    "offs": ["하차총승객수", "하차", "offs", "하차수"],
}

col_map = {}
missing_expected = []

for key, variants in expected.items():
    found = False
    for v in variants:
        nv = norm(v)
        if nv in normalized:
            col_map[key] = normalized[nv]
            found = True
            break
    if not found:
        # try fuzzy by checking substring matches
        for nkey, orig in normalized.items():
            for v in variants:
                if v.lower() in nkey:
                    col_map[key] = orig
                    found = True
                    break
            if found:
                break
    if not found:
        missing_expected.append(key)

if missing_expected:
    st.warning(f"필수 컬럼 매핑에 실패한 항목: {missing_expected}")
    st.info("현재 컬럼명을 확인해주세요:")
    st.write(orig_cols)
    # allow user to manually map
    st.markdown("수동 매핑: (없으면 취소)")
    manual = {}
    for key in missing_expected:
        sel = st.selectbox(f"{key} 컬럼으로 사용할 컬럼을 선택하세요 (취소하려면 '선택안함')", options=["선택안함"] + orig_cols, key=key)
        if sel != "선택안함":
            manual[key] = sel
    for k, v in manual.items():
        col_map[k] = v

# Now check final mapping
required_keys = ["date", "line", "station", "ons", "offs"]
if not all(k in col_map for k in required_keys):
    st.error("필수 컬럼이 모두 매핑되지 않았습니다. 앱을 종료합니다.")
    st.stop()

# rename for convenience
df = df.rename(columns={col_map[k]: k for k in col_map})

# show head if debug
if show_debug:
    st.subheader("데이터 샘플 (처음 10행)")
    st.dataframe(df.head(10))

# ------------------------------
# 날짜 파싱: 여러 포맷 시도
# ------------------------------
def parse_dates(s):
    # try YYYYMMDD numeric-ish
    try:
        return pd.to_datetime(s.astype(str), format="%Y%m%d", errors="coerce")
    except Exception:
        pass
    # try general parse
    return pd.to_datetime(s, errors="coerce", infer_datetime_format=True)

try:
    df["date_parsed"] = parse_dates(df["date"])
except Exception as e:
    st.exception(e)
    st.stop()

if df["date_parsed"].isna().all():
    st.error("날짜 파싱에 실패했습니다. 'date' 컬럼의 형식을 확인해주세요.")
    st.write("date 컬럼 샘플:")
    st.write(df["date"].astype(str).unique()[:20])
    st.stop()

df["date_only"] = df["date_parsed"].dt.date

# ------------------------------
# 숫자 변환: ons/offs
# ------------------------------
for c in ["ons", "offs"]:
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)

df["sum"] = df["ons"] + df["offs"]

# ------------------------------
# UI: 날짜/호선 선택
# ------------------------------
available_dates = sorted(df["date_only"].dropna().unique())
available_lines = sorted(df["line"].dropna().unique())

if not available_dates.any():
    st.error("사용 가능한 날짜가 없습니다.")
    st.stop()

st.sidebar.subheader("필터")
selected_date = st.sidebar.date_input("날짜 선택", value=available_dates[0], min_value=min(available_dates), max_value=max(available_dates))
selected_line = st.sidebar.selectbox("호선 선택 (전체 포함)", options=["전체"] + available_lines, index=0)

# ------------------------------
# 필터링
# ------------------------------
filtered = df[df["date_only"] == selected_date]
if selected_line != "전체":
    filtered = filtered[filtered["line"] == selected_line]

if filtered.empty:
    st.warning("해당 조건에 맞는 데이터가 없습니다.")
    st.write("가능한 날짜 예시 (상위 10):", available_dates[:10])
    st.write("가능한 호선 예시 (상위 10):", available_lines[:10])
    st.stop()

top10 = filtered.sort_values("sum", ascending=False).head(10).reset_index(drop=True)

# ------------------------------
# 색상: 1등 빨강, 나머지 그라데이션 블루
# ------------------------------
colors = []
if len(top10) > 0:
    colors.append("#ff0000")
for i in range(1, len(top10)):
    alpha = max(0.15, 1 - 0.12 * i)
    colors.append(f"rgba(13,110,237,{alpha})")  # bootstrap blue-ish

# ------------------------------
# Plotly 그리기
# ------------------------------
try:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top10["station"],
        y=top10["sum"],
        marker=dict(color=colors),
        text=[f"승차: {a:,}<br>하차: {b:,}<br>합계: {c:,}" for a,b,c in zip(top10["ons"], top10["offs"], top10["sum"])],
        hoverinfo="text"
    ))
    fig.update_layout(
        title=f"{selected_date} — {selected_line} 승하차 합계 TOP10",
        xaxis_title="역명",
        yaxis_title="승하차 합계",
        xaxis_tickangle=-40,
        margin=dict(l=40, r=20, t=70, b=120),
    )
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.exception(e)
    if show_debug:
        st.text(traceback.format_exc())

# ------------------------------
# 데이터 테이블과 디버그 출력
# ------------------------------
st.subheader("상위 10개 역 데이터")
display_df = top10[["date_parsed", "line", "station", "ons", "offs", "sum"]].copy()
display_df["date_parsed"] = display_df["date_parsed"].dt.strftime("%Y-%m-%d")
st.dataframe(display_df.style.format({"ons":"{:,}", "offs":"{:,}", "sum":"{:,}"}), height=320)

if show_debug:
    st.subheader("디버그 정보")
    st.write("사용된 CSV 경로:", used_path)
    st.write("원본 컬럼:", orig_cols)
    st.write("매핑된 컬럼 (표준명 -> 원본):", col_map)
    st.write("로드된 행 수:", len(df))
    st.write("샘플 데이터 타입:")
    st.write(df.dtypes.astype(str))
