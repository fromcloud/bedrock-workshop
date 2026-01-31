# Streamlit 요소를 사용하고 백엔드 라이브러리 스크립트의 함수를 입수합니다.
import streamlit as st 
import rag_chatbot_lib as glib


# 페이지 제목과 구성을 추가합니다.
st.set_page_config(page_title="RAG Chatbot") 
st.title("RAG Chatbot") 

# UI 채팅 기록을 세션 캐시에 추가합니다.
if 'chat_history' not in st.session_state: #see if the chat history hasn't been created yet
    st.session_state.chat_history = [] #initialize the chat history

# 채팅 입력 컨트롤을 추가합니다.
chat_container = st.container()

input_text = st.chat_input("Chat with your bot here") #display a chat input box

if input_text:
    glib.chat_with_model(message_history=st.session_state.chat_history, new_text=input_text)


# 이전 채팅 메시지를 렌더링하는 for 루프를 추가합니다.
# 채팅 기록을 다시 렌더링합니다 (Streamlit은 이 스크립트를 다시 실행하므로 이전 채팅 메시지를 보존하려면 이 작업이 필요합니다).
for message in st.session_state.chat_history: #loop through the chat history
    with chat_container.chat_message(message.role): #renders a chat line for the given role, containing everything in the with block
        st.markdown(message.text) #display the chat content