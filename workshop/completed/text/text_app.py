import streamlit as st # 모든 streamlit 명령을 "st" 별칭을 통해 사용할 수 있습니다.
import text_lib as glib # 로컬 라이브러리 스크립트에 대한 참조

# 페이지 제목과 구성을 추가합니다.
st.set_page_config(page_title="Text to Text") #HTML title
st.title("Text to Text") #page title

# 입력 요소를 추가합니다. 
input_text = st.text_area("Input text", label_visibility="collapsed") 
go_button = st.button("Go", type="primary")

# 출력 요소를 추가합니다.
if go_button: 
    with st.spinner("Working..."): 
        response_content = glib.get_text_response(input_content=input_text) 
        st.write(response_content)
