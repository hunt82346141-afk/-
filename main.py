import streamlit as st  
st.title("나의 웹 서비스 만들기!!")
name=st.text_input('이름을 알려주세요:')
 st.selectbox('좋아하는 음식을 선택해주세요:',['니애미','니애비'])
if st.button('인사말 생성'):
  st.info(name+'님 안녕하세요')
  st.warning('반가워요')
  st.error('정말 반가워요')
  st.balloons()
