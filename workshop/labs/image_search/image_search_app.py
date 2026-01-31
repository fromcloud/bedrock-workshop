import streamlit as st #모든 streamlit 명령을 st 별칭을 통해 사용할 수 있습니다.
import image_search_lib as glib #로컬 라이브러리 스크립트에 대한 참조


st.set_page_config(page_title="이미지 검색", layout="wide") #HTML title
st.title("이미지 검색") #page title

# 탭 레이아웃을 초기화합니다.
search_images_tab, find_similar_images_tab = st.tabs(["이미지 검색", "유사한 이미지 찾기"])

# 이미지 검색 모드의 요소를 추가합니다.
with search_images_tab:

    search_col_1, search_col_2 = st.columns(2)

    with search_col_1:
        input_text = st.text_input("검색어를 입력하세요") #레이블이 없는 여러 줄 텍스트 상자를 표시합니다.
        search_button = st.button("검색", type="primary") #기본 버튼 표시

    with search_col_2:
        if search_button: #버튼이 클릭될 때 이 if 블록의 코드가 실행됩니다.
            st.subheader("검색 결과")
            with st.spinner("검색중..."): #이 블록의 코드가 실행되는 동안 스피너를 표시합니다.
                response_content = glib.get_similarity_search_results(search_term=input_text)
                
                for res in response_content:
                    st.image(res, width=250)


# 유사한 이미지 찾기 모드의 요소를 추가합니다
with find_similar_images_tab:
    
    find_col_1, find_col_2 = st.columns(2)

    with find_col_1:
    
        uploaded_file = st.file_uploader("이미지 파일 선택", type=['png', 'jpg'])
        
        if uploaded_file:
            uploaded_image_preview = uploaded_file.getvalue()
            st.image(uploaded_image_preview)
    
        find_button = st.button("유사한 이미지 찾기", type="primary") #기본 버튼 표시

    with find_col_2:
        if find_button: #버튼이 클릭될 때 이 if 블록의 코드가 실행됩니다.
            st.subheader("유사한 이미지")
            with st.spinner("검색중..."): #이 블록의 코드가 실행되는 동안 스피너를 표시합니다.
                response_content = glib.get_similarity_search_results(search_image=uploaded_file.getvalue())
                
                for res in response_content:
                    st.image(res, width=250)