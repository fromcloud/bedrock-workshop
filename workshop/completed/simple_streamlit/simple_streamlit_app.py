# import 문을 추가합니다. : 이 문장을 통해 Streamlit 요소와 함수를 사용할 수 있습니다.
import streamlit as st 


# 페이지 제목과 구성을 추가합니다. : 여기서는 실제 페이지의 제목과 브라우저 탭에 표시되는 제목을 설정합니다.
st.set_page_config(page_title="Streamlit Demo") #HTML title
st.title("Streamlit Demo") #page title


# 사용자 입력 요소를 추가합니다. : 사용자로부터 색상을 입력받기 위한 텍스트 상자와 버튼을 만듭니다.
color_text = st.text_input("What's your favorite color?") #display a text box
go_button = st.button("Go", type="primary") #display a primary button


# 출력 요소를 추가합니다. : 아래의 if 블록은 버튼이 클릭되었을 때 동작합니다. 
if go_button: #code in this if block will be run when the button is clicked
    st.write(f"I like {color_text} too!") #display the response content
