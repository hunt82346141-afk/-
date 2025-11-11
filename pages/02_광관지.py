import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit.components.v1 import html

# -------------------------------
# 관광지 데이터 (이름, 위도, 경도, 설명, 지하철역)
# -------------------------------
places = [
    ("경복궁", 37.577609, 126.976978, "조선 시대의 법궁으로, 서울의 대표 고궁입니다.", "경복궁역 (3호선)"),
    ("N서울타워", 37.551233, 126.988205, "남산 정상에 위치한 전망타워로, 서울 전경을 한눈에 볼 수 있습니다.", "명동역 (4호선)"),
    ("명동", 37.564213, 126.982473, "서울의 대표 쇼핑 거리로 외국인 관광객들에게 가장 인기 있는 명소입니다.", "명동역 (4호선)"),
    ("롯데월드타워", 37.513383, 127.101086, "123층 초고층 타워로, 전망대 ‘서울스카이’와 롯데월드몰이 있습니다.", "잠실역 (2·8호선)"),
    ("청계천", 37.571093, 126.977019, "서울 도심을 가로지르는 복원된 하천으로, 산책과 야경 감상 명소입니다.", "광화문역 (5호선)"),
    ("북촌한옥마을", 37.582346, 126.983028, "전통 한옥이 모여 있는 마을로, 한국의 전통문화를 체험할 수 있습니다.", "안국역 (3호선)"),
    ("광화문", 37.573609, 126.976979, "대한민국의 상징적인 광장으로, 세종대왕 동상과 이순신 장군 동상이 있습니다.", "광화문역 (5호선)"),
    ("서울숲", 37.544702, 127.037273, "도심 속 자연 휴식 공간으로, 자전거도로와 동물원, 전시장이 있습니다.", "뚝섬역 (2호선)"),
    ("한강공원", 37.530826, 126.993223, "서울의 대표적인 시민공원으로, 자전거 타기와 야경 감상이 인기입니다.", "여의나루역 (5호선)"),
    ("동대문디자인플라자 (DDP)", 37.566557, 127.009138, "현대적 건축물로 패션, 전시, 야시장 등 다양한 문화가 공존합니다.", "동대문역사문화공원역 (2·4·5호선)")
]

# -------------------------------
# Streamlit 기본 UI
# -------------------------------
st.title("🌏 서울 주요 관광지 TOP 10")
st.write("관광지 이름을 선택하면 지도에서 해당 위치로 이동하고, 마우스를 올리면 이름이 가로로 표시됩니다.")

# 선택 기능
place_names = [p[0] for p in places]
selected_place = st.selectbox("📍 보고 싶은 관광지를 선택하세요", place_names)

# 선택된 관광지 좌표 가져오기
selected_data = next(p for p in places if p[0] == selected_place)
selected_lat, selected_lon = selected_data[1], selected_data[2]

# -------------------------------
# 지도 생성
# -------------------------------
m = folium.Map(location=[selected_lat, selected_lon], zoom_start=14)
marker_cluster = MarkerCluster().add_to(m)

# 마커 추가
for name, lat, lon, desc, subway in places:
    tooltip_html = f"<div style='white-space: nowrap;'>{name}</div>"  # 👉 이름 가로로 표시
    folium.Marker(
        [lat, lon],
        popup=f"<b>{name}</b><br>{desc}<br><i>🚇 {subway}</i>",
        tooltip=tooltip_html,
        icon=folium.Icon(
            color="red" if name == selected_place else "blue",
            icon="star" if name == selected_place else "info-sign"
        )
    ).add_to(marker_cluster)

# Folium 지도 HTML 변환
map_html = m._repr_html_()

# -------------------------------
# 지도 출력 (크기 축소)
# -------------------------------
st.write("🗺️ 선택한 관광지 위치 지도")
html(map_html, height=330)

# -------------------------------
# 관광지 설명
# -------------------------------
st.markdown("---")
st.subheader("📍 관광지 소개")
st.markdown(f"### 🏙️ {selected_data[0]}")
st.write(selected_data[3])
st.write(f"**🚇 가까운 전철역:** {selected_data[4]}")

# 전체 리스트 보기
with st.expander("🔽 전체 관광지 목록 보기"):
    for name, lat, lon, desc, subway in places:
        st.markdown(f"**{name}** — {desc} (🚇 {subway})")
