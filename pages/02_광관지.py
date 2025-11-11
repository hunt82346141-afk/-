import streamlit as st
import folium
from folium.plugins import MarkerCluster

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

# 스트림릿 웹페이지 제목 설정
st.title("서울 주요 관광지 TOP 10")

# 지도 생성 (서울 중심)
m = folium.Map(location=[37.5665, 126.9780], zoom_start=12)

# 마커 클러스터 설정
marker_cluster = MarkerCluster().add_to(m)

# 관광지 마커 추가
for place in places:
    folium.Marker(
        location=[place[1], place[2]],
        popup=place[0],
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(marker_cluster)

# 스트림릿에서 지도 표시
st.write("서울 주요 관광지 지도")
st.dataframe(places)  # 관광지 데이터 표로 보여주기
st.markdown(folium.Figure(width=700, height=500).add_child(m)._repr_html_(), unsafe_allow_html=True)

