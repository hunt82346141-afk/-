# streamlit_app.py
import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="MBTI 책 & 영화 추천 🎬📚", page_icon="💫", layout="centered")

# 제목
st.title("🌟 MBTI로 알아보는 인생책 & 인생영화 추천 🎯")
st.markdown("MBTI를 고르면 ✨ 당신의 성향에 어울리는 **책 2권**과 **영화 2편**을 센스있게 추천해드릴게요 💬")

# MBTI 목록
mbti_list = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP"
]

# MBTI별 추천 데이터
recommendations = {
    "INTJ": {
        "books": ["『1984』 — 조지 오웰", "『The Martian』 — 앤디 위어"],
        "movies": ["🎞️ Inception (2010)", "🧠 The Imitation Game (2014)"],
        "desc": "전략적 사고와 분석력이 뛰어난 당신에게, 생각의 깊이를 더해줄 작품들이에요."
    },
    "INTP": {
        "books": ["『Gödel, Escher, Bach』 — 더글라스 호프스태터", "『The Name of the Rose』 — 움베르토 에코"],
        "movies": ["🌀 The Matrix (1999)", "🌌 Arrival (2016)"],
        "desc": "논리와 철학을 사랑하는 INTP, 복잡한 세계 속 진리를 탐구할 작품들이죠!"
    },
    "ENTJ": {
        "books": ["『Good to Great』 — 짐 콜린스", "『Atlas Shrugged』 — 에인 랜드"],
        "movies": ["💼 The Social Network (2010)", "🎯 Moneyball (2011)"],
        "desc": "리더십과 목표 지향적인 당신에게, 야망과 전략이 빛나는 이야기들이 어울려요!"
    },
    "ENTP": {
        "books": ["『The Lean Startup』 — 에릭 리스", "『Surely You're Joking, Mr. Feynman!』 — 리처드 파인만"],
        "movies": ["🚀 The Big Short (2015)", "🎭 Catch Me If You Can (2002)"],
        "desc": "창의력 넘치는 당신에게, 혁신과 도전의 에너지가 가득한 이야기들을 선물할게요!"
    },
    "INFJ": {
        "books": ["『The Alchemist』 — 파울로 코엘료", "『To Kill a Mockingbird』 — 하퍼 리"],
        "movies": ["🕊️ Dead Poets Society (1989)", "💫 Amélie (2001)"],
        "desc": "이상과 진심을 추구하는 INFJ, 마음을 울리고 영감을 주는 작품이에요."
    },
    "INFP": {
        "books": ["『The Little Prince』 — 생텍쥐페리", "『Norwegian Wood』 — 무라카미 하루키"],
        "movies": ["💭 Eternal Sunshine of the Spotless Mind (2004)", "🌆 Lost in Translation (2003)"],
        "desc": "감수성 풍부한 INFP에게 어울리는, 감정과 아름다움이 흐르는 이야기예요."
    },
    "ENFJ": {
        "books": ["『Man’s Search for Meaning』 — 빅터 프랭클", "『The Four Agreements』 — 돈 미겔 루이스"],
        "movies": ["🌻 The Pursuit of Happyness (2006)", "💬 The Intern (2015)"],
        "desc": "사람을 이끌고 돕는 따뜻한 당신에게, 영감을 주는 이야기들을 골랐어요!"
    },
    "ENFP": {
        "books": ["『Big Magic』 — 엘리자베스 길버트", "『The Hitchhiker’s Guide to the Galaxy』 — 더글러스 애덤스"],
        "movies": ["🌈 Little Miss Sunshine (2006)", "🎡 La La Land (2016)"],
        "desc": "열정과 자유를 사랑하는 ENFP, 당신의 반짝이는 에너지에 꼭 어울리는 작품들이에요!"
    },
    "ISTJ": {
        "books": ["『The Road』 — 코맥 매카시", "『The Seven Habits of Highly Effective People』 — 스티븐 코비"],
        "movies": ["🕵️ Bridge of Spies (2015)", "📋 Spotlight (2015)"],
        "desc": "성실하고 책임감 있는 ISTJ, 원칙과 현실 속에서 빛나는 인물들을 만나보세요."
    },
    "ISFJ": {
        "books": ["『Pride and Prejudice』 — 제인 오스틴", "『The Help』 — 캐서린 스토켓"],
        "movies": ["👑 The King’s Speech (2010)", "💖 Hidden Figures (2016)"],
        "desc": "따뜻하고 세심한 ISFJ에게 어울리는, 감동과 인간미 넘치는 이야기예요."
    },
    "ESTJ": {
        "books": ["『Team of Rivals』 — 도리스 컨스 굿윈", "『The 48 Laws of Power』 — 로버트 그린"],
        "movies": ["🏛️ A Few Good Men (1992)", "📈 Remember the Titans (2000)"],
        "desc": "실행력과 리더십이 강한 ESTJ, 현실적인 성취와 원칙이 돋보이는 작품이에요."
    },
    "ESFJ": {
        "books": ["『The Secret』 — 론다 번", "『The Joy Luck Club』 — 에이미 탠"],
        "movies": ["🎀 The Holiday (2006)", "🎶 Mamma Mia! (2008)"],
        "desc": "사람을 아끼고 함께하는 걸 좋아하는 ESFJ, 따뜻한 관계를 그린 이야기예요."
    },
    "ISTP": {
        "books": ["『The Art of War』 — 손자", "『Into Thin Air』 — 존 크라카우어"],
        "movies": ["⚙️ Drive (2011)", "🔥 Mad Max: Fury Road (2015)"],
        "desc": "문제를 해결하고 도전하는 걸 좋아하는 ISTP, 역동적이고 분석적인 작품이에요."
    },
    "ISFP": {
        "books": ["『The Nightingale』 — 크리스틴 해나", "『On the Road』 — 잭 케루악"],
        "movies": ["💐 Call Me by Your Name (2017)", "🎨 Her (2013)"],
        "desc": "감각적이고 감성적인 ISFP에게, 아름다움과 감정이 가득한 이야기예요."
    },
    "ESTP": {
        "books": ["『Born to Run』 — 크리스토퍼 맥두걸", "『Shoe Dog』 — 필 나이트"],
        "movies": ["💬 The Wolf of Wall Street (2013)", "🏎️ Baby Driver (2017)"],
        "desc": "활동적이고 모험을 즐기는 ESTP, 에너지 넘치는 작품으로 자극받아봐요!"
    },
    "ESFP": {
        "books": ["『Eat Pray Love』 — 엘리자베스 길버트", "『Crazy Rich Asians』 — 케빈 콴"],
        "movies": ["🎉 Ocean’s Eleven (2001)", "🌟 The Greatest Showman (2017)"],
        "desc": "생기 넘치고 매력적인 ESFP에게 어울리는, 반짝이고 즐거운 이야기예요!"
    },
}

# 사용자 입력
choice = st.selectbox("당신의 MBTI는? 💬", mbti_list, index=7)

# 버튼 클릭 시 결과 출력
if st.button("추천 보기 💫"):
    rec = recommendations.get(choice)
    st.markdown(f"## 💡 {choice} 타입에게 어울리는 책 & 영화 추천 💡")
    st.markdown("### 📚 책 추천")
    for b in rec["books"]:
        st.write(f"- {b}")
    st.markdown("### 🎬 영화 추천")
    for m in rec["movies"]:
        st.write(f"- {m}")
    st.divider()
    st.info(f"✨ {rec['desc']}")

# 하단 문구
st.markdown("---")
st.caption("Made with ❤️ by ChatGPT | 원하면 각 책·영화의 줄거리 요약이나 평점도 추가해드릴게요 🌈")
