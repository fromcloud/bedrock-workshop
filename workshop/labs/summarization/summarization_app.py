import streamlit as st
import summarization_lib as glib

st.set_page_config(page_title="Document Summarization")
st.title("Document Summarization")


# 문서는 자동으로 백그라운드에서 로드됩니다.
# 텍스트 상자를 통해 사용자가 요약의 초점을 안내할 수 있습니다.
# 아래의 if 블록을 사용하여 버튼 클릭을 처리합니다. 백엔드 함수가 호출되는 동안 스피너를 표시한 다음 출력을 웹 페이지에 작성합니다.
input_text = st.text_area("How would you like the document summarized?")

summarize_button = st.button("Summarize", type="primary")

if summarize_button:
    st.subheader("Summary")

    with st.spinner("Running..."):
        response_content = glib.get_summary(input_text)
        st.write(response_content)

