import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json

# ==============================================================================
# 1. 데이터 로드 및 전처리
# ==============================================================================

# 파일 이름 (업로드된 CSV 파일)
DATA_FILE = "인공지는 수행.csv"

@st.cache_data
def load_and_preprocess_data(file_path):
    """CSV 파일을 로드하고 분석에 맞게 전처리합니다."""
    try:
        # 파일 인코딩 문제 해결을 위해 'cp949' 또는 'euc-kr' 시도
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='cp949')

        # 첫 두 열을 인덱스로 설정 (범죄대분류, 범죄중분류)
        df_data = df.set_index(['범죄대분류', '범죄중분류'])
        
        # 숫자 데이터가 아닌 열은 제외 및 NaN 값은 0으로 채우기
        df_numeric = df_data.apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)
        
        # 지역별 총 범죄 건수 계산
        district_totals = df_numeric.sum().sort_values(ascending=False).to_frame(name='총 범죄 건수')
        
        return df_numeric, district_totals
    except Exception as e:
        st.error(f"⚠️ 데이터 로드 및 전처리 중 심각한 오류가 발생했습니다: {e}")
        return None, None

# 데이터 로드
crime_df, crime_totals = load_and_preprocess_data(DATA_FILE)

# ==============================================================================
# 2. 지역 정보 (위도, 경도) 설정 🚨 사용자 입력 필수
# ==============================================================================
# 🚨 주의: 이 데이터는 지도 표시를 위해 사용자께서 직접 채워주셔야 합니다.
# '지역명'은 CSV 파일의 컬럼명과 정확히 일치해야 합니다.
# 현재는 서울 중심 및 일부 지역만 임의로 채워 넣어두었습니다.
district_lat_lon = {
    # 서울 지역 (일부)
    "서울종로구": [37.5750, 126.9800], "서울중구": [37.5638, 126.9975], "서울용산구": [37.5325, 126.9902],
    "서울성동구": [37.5633, 127.0366], "서울광진구": [37.5385, 127.0820], "서울동대문구": [37.5744, 127.0396],
    "서울강남구": [37.5172, 127.0473], "서울송파구": [37.5145, 127.1060], "서울강동구": [37.5301, 127.1238],
    
    # 부산 지역 (예시)
    "부산중구": [35.1018, 129.0234], "부산서구": [35.0934, 129.0108], "부산동구": [35.1328, 129.0436],
    
    # 대구 지역 (예시)
    "대구중구": [35.8679, 128.6010], "대구동구": [35.8829, 128.6940], "대구서구": [35.8722, 128.5630],
    "대구남구": [35.8450, 128.5860], "대구북구": [35.8790, 128.5870], "대구수성구": [35.8620, 128.6500],
    "대구달서구": [35.8360, 128.5300], "대구달성군": [35.8790, 128.4350], "대구군위군": [36.2300, 128.5800],
    
    # ⚠️ CSV 파일에 있는 모든 지역의 좌표를 여기에 추가하세요! 
    # 예: "인천연수구": [37.4069, 126.6787], "광주광산구": [35.1764, 126.8049], ...
}

# 지역 이름을 깔끔하게 정리하는 함수 ('서울종로구' -> '종로구')
def clean_district_name(full_name):
    """시/도 명칭을 제거합니다."""
    for city in ["서울", "부산", "대구", "인천", "광주", "대전", "울산"]:
        if full_name.startswith(city):
            return full_name.replace(city, '')
    return full_name

# ==============================================================================
# 3. Streamlit 앱 레이아웃 및 초기화
# ==============================================================================
st.set_page_config(layout="wide")
st.title("🛡️ 대한민국 지역별 범죄 안전 지표 (위험도 시각화)")
st.markdown("---")

if crime_df is None or crime_totals is None:
    st.error("데이터를 불러오거나 처리하는 데 문제가 있어 앱을 실행할 수 없습니다. CSV 파일 구조를 확인해주세요.")
    st.stop()

# 초기 상태 설정
if 'selected_district' not in st.session_state:
    # 총 범죄 건수가 가장 많은 지역을 초기값으로 설정
    default_district = crime_totals.index[0] if len(crime_totals.index) > 0 else "서울종로구"
    st.session_state.selected_district = default_district

# ==============================================================================
# 4. 지도 생성 및 클릭 이벤트 처리 (CircleMarker로 지역 위험도 시각화)
# ==============================================================================
def create_interactive_crime_map():
    """Folium 지도를 생성하고 지역별 범죄 건수에 따라 원의 크기와 색상을 조정하여 표시합니다."""
    
    if not district_lat_lon:
        st.warning("🚨 지역 좌표 데이터가 없어 지도를 표시할 수 없습니다. '사용자 지침 사항'을 확인해주세요.")
        return 

    # 현재 선택된 지역을 지도 중앙으로 설정
    current_district = st.session_state.selected_district
    if current_district in district_lat_lon:
        center_lat, center_lon = district_lat_lon[current_district]
    else:
        # 기본값 (서울 중심)
        center_lat, center_lon = 37.5665, 126.9780 

    # Folium 맵 생성
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles="cartodbpositron")

    # 범죄 건수 스케일링을 위한 최소/최대값 계산
    total_crime_counts = crime_totals['총 범죄 건수'].values
    
    # 맵에 표시되는 지역의 범죄 건수만 사용
    valid_counts = total_crime_counts[pd.Series(crime_totals.index).isin(district_lat_lon.keys())].values
    
    if len(valid_counts) > 0:
        min_crime = valid_counts.min()
        max_crime = valid_counts.max()
    else:
        min_crime, max_crime = 0, 1 # Prevent division by zero

    def scale_crime_value(value):
        """범죄 건수를 맵 마커 크기 및 색상으로 스케일링합니다."""
        if max_crime == min_crime:
            return 8, 'blue' # Default size/color if all values are the same
        
        # Normalize (0 to 1)
        norm = (value - min_crime) / (max_crime - min_crime)
        
        # Radius scaling (Min radius 8, Max radius 30) -> 범죄가 많을수록 원이 커집니다.
        radius = 8 + norm * 22 
        
        # Color scaling (Red for high crime, Green for low crime) -> 범죄가 많을수록 붉어집니다.
        if norm > 0.7:
            color = 'red' # 위험
        elif norm > 0.4:
            color = 'orange' # 주의
        else:
            color = 'green' # 안전

        return radius, color

    # 지역별 CircleMarker 추가
    for district, [lat, lon] in district_lat_lon.items():
        if district not in crime_totals.index:
            continue
            
        total_crime = crime_totals.loc[district, '총 범죄 건수']
        radius, marker_color = scale_crime_value(total_crime)
        
        is_selected = (district == current_district)
        
        # 팝업에 특별한 클래스를 추가하여 Streamlit에서 클릭 이벤트를 잡을 수 있도록 함
        # 이 부분이 지도에서 클릭 시 하단 정보가 업데이트되는 핵심입니다.
        popup_html = f"""
            <div 
                onclick="window.parent.postMessage({{'type': 'streamlit:setComponentValue', 'key': 'clicked_district_key', 'value': '{district}', 'is_user_triggered': true}}, '*')" 
                style='cursor: pointer; font-weight: bold; padding: 5px; text-align: center;'>
                {clean_district_name(district)}<br> 👈 분석 보기
            </div>
        """
        
        # CircleMarker 사용: 크기와 색상으로 위험도 시각화
        folium.CircleMarker(
            [lat, lon],
            radius=radius,
            color='black', # 외곽선 색상
            weight=1, # 외곽선 두께
            fill=True,
            # 선택된 지역은 강조를 위해 빨간색으로 고정
            fill_color='red' if is_selected else marker_color, 
            fill_opacity=0.6,
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=f"{clean_district_name(district)} | 🚨 총 범죄: {total_crime:,}건 (크기=위험도)",
        ).add_to(m) # 지도에 직접 추가

    # st_folium을 사용하여 지도를 표시하고 클릭 데이터를 받습니다.
    st.subheader("🗺️ 지역 위험도 시각화 지도 (원 크기/색상 = 범죄 건수)")
    map_output = st_folium(
        m, 
        width=1000, 
        height=450, 
        key="crime_map", 
        return_on_hover=False, 
        # Streamlit 컴포넌트 값을 저장하기 위한 더미 키
        component_key="clicked_district_key" 
    )

    # 클릭 이벤트 처리 (map_output이 아닌, st.session_state에 저장된 값을 이용)
    clicked_district = st.session_state.get('clicked_district_key')
    
    if clicked_district and clicked_district != st.session_state.selected_district:
        st.session_state.selected_district = clicked_district
        # 상태가 변경되었으므로 Streamlit을 재실행하여 하단 목록 업데이트 및 지도 중심 변경
        st.rerun() 

# ==============================================================================
# 5. 메인 앱 실행 및 분석 결과 표시
# ==============================================================================
col_map, col_controls = st.columns([7, 3])

with col_controls:
    st.subheader("📊 지역 선택 및 요약")
    
    # 지역 선택 셀렉트 박스 (지도 클릭과 동기화됨)
    district_list = list(crime_df.columns)
    
    # 현재 선택된 지역을 기준으로 셀렉트 박스 인덱스 설정
    default_index = district_list.index(st.session_state.selected_district) if st.session_state.selected_district in district_list else 0
    
    new_selection = st.selectbox(
        "🔎 지도 영역 밖의 지역 검색", 
        district_list,
        index=default_index,
        format_func=clean_district_name,
        key="selectbox_district"
    )
    
    # 셀렉트 박스 변경 시 세션 상태 업데이트 및 지도 업데이트를 위해 재실행
    if new_selection != st.session_state.selected_district:
        st.session_state.selected_district = new_selection
        st.session_state.clicked_district_key = new_selection # 지도의 중심을 변경하기 위한 꼼수
        st.rerun()

    st.subheader(f"✨ {clean_district_name(st.session_state.selected_district)} 안전 지표")
    
    total_crime_count = crime_totals.loc[st.session_state.selected_district, '총 범죄 건수']
    st.metric(
        label="총 범죄 발생 건수 (202X년 기준)", 
        value=f"{total_crime_count:,} 건",
        delta="🚨 지도에서 원이 클수록, 붉을수록 위험도가 높습니다.",
        delta_color="off" # 델타 색상 비활성화
    )
    
    st.info("👆 지도에서 **원(마커)**을 클릭하거나 검색창을 이용해 지역을 선택하세요.", icon="📌")

with col_map:
    # 지도 생성 및 표시
    create_interactive_crime_map()


# ==============================================================================
# 6. 선택된 지역의 상세 범죄 목록 표시
# ==============================================================================

st.markdown("---")
st.subheader(f"🔍 {clean_district_name(st.session_state.selected_district)} 상세 범죄 현황")
st.markdown("👇 범죄 대분류 및 중분류별 발생 건수입니다. 건수가 많을수록 배경색이 진해집니다.")


# 선택된 지역의 데이터 추출 및 정렬
try:
    district_data = crime_df[st.session_state.selected_district]
    
    # 2단계 인덱스(대분류, 중분류)를 사용하여 DataFrame으로 변환하고 정렬
    district_analysis_df = district_data.to_frame(name='발생 건수')
    district_analysis_df.index.names = ['대분류', '중분류']
    
    # 발생 건수를 기준으로 내림차순 정렬
    district_analysis_df = district_analysis_df.sort_values(by='발생 건수', ascending=False)
    
    # 스타일링 적용 (센스있는 이모티콘 및 색상)
    def color_high_crime(val):
        """건수가 높을수록 붉은색 배경을 적용하는 함수"""
        if isinstance(val, (int, float)) and val > 0:
            max_val = district_analysis_df['발생 건수'].max()
            norm = val / max_val if max_val > 0 else 0
            # 강한 범죄일수록 붉은색 농도 증가
            return f'background-color: rgba(255, 99, 71, {norm * 0.4})'
        return ''

    styled_df = district_analysis_df.style.applymap(color_high_crime, subset=['발생 건수'])
    
    st.dataframe(
        styled_df, 
        use_container_width=True,
        height=400
    )

    st.markdown("### 🏆 주요 범죄 Top 5 요약")
    
    # 범죄대분류별 합계 요약
    crime_summary = district_data.groupby(level='범죄대분류').sum().sort_values(ascending=False)
    
    # 이모티콘 매핑
    emoji_map = {
        '절도': '💸', '폭력': '🤕', '강도': '🔪', '살인': '⚰️', 
        '성폭력': '🚫', '지능': '🧠', '재산범죄': '💰', 
        '교통범죄': '🚗', '기타': '💡'
    }

    cols = st.columns(min(len(crime_summary), 5))
    for i, (category, count) in enumerate(crime_summary.head(5).items()):
        emoji = emoji_map.get(category, '📝')
        with cols[i]:
            st.metric(
                label=f"{emoji} {category}", 
                value=f"{count:,} 건"
            )

except KeyError:
    st.error(f"선택된 지역 ({st.session_state.selected_district})에 해당하는 데이터가 CSV 파일에 없습니다. 파일 내용을 확인해주세요.")
except Exception as e:
    st.error(f"데이터 시각화 중 오류가 발생했습니다: {e}")

st.markdown("---")
st.caption("✨ 분석 시스템 정보: Streamlit, Pandas, Folium 기반. 데이터 출처: 인공지는 수행.csv")
