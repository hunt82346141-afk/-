import streamlit as st  
st.title("나의 웹 서비스 만들기!!")
name=st.text_input('이름을 알려주세요:')
menu=st.selectbox('좋아하는 음식을 선택해주세요:',['스시','오꼬노마야끼'])
if st.button('인사말 생성'):
  st.info(name+'님 안녕하세요')
  st.warning(menu+'를 좋아하시나봐요 저는 싫어하는데')
  st.error('정말 반가워요')
  st.balloons()
