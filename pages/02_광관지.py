import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit.components.v1 import html

# 서울의 주요 관광지 리스트 (위도, 경도, 관광지 이름)
places = [
    ("경복궁", 37.577609, 126.976978),
    ("N서울타워", 37.551233, 126.988205),
    ("명동", 37.564213, 126.982473),
    ("롯데월드타워", 37.513383, 127.101086),
    ("청계천", 37.571093, 126.977019),
    ("북촌한옥마을", 37.582346, 126.983028),
    ("광화문", 37.573609, 126.976979),
    ("서울숲", 37.544702, 127.037273),
    ("한강공원", 37.530826, 126.993223),
    ("동대문디자인플라자", 37.566557, 127.009138)
]

# 스트림릿 제목
st.title("🌏 서울 주요 관광지 TOP 10")
st.write("외국인 관광객이 많이 찾는 서울의 대표 명소들을 지도에 표시했습니다!")

# 지도 생성
m = folium.Map(location=[37.5665, 126.9780], zoom_start=12)
marker_cluster = MarkerCluster().add_to(m)

# 마커 추가
for name, lat, lon in places:
    folium.Marker(
        [lat, lon],
        popup=name,
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(marker_cluster)

# Folium 지도를 HTML로 변환
map_html = m._repr_html_()

# 스트림릿에서 표시
st.dataframe(places, column_config={
    0: "관광지 이름",
    1: "위도",
    2: "경도"
})
st.write("🗺️ 관광지 위치 지도:")
html(map_html, height=500)
