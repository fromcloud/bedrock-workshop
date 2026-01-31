import streamlit as st
import image_understanding_lib as glib

st.set_page_config(layout="wide", page_title="Image Understanding")

st.title("Image Understanding")

col1, col2, col3 = st.columns(3)

prompt_options_dict = {
    "이미지 제목": "이 이미지에 대한 간략한 제목을 한글로 제공해 주세요.",
    "상세 묘사": "이 이미지에 대한 자세한 설명을 한글로 제공해 주세요.",
    "이미지 분류": "이 이미지를 다음 범주 중 하나로 분류해 주세요: 사람, 음식, 기타. 범주 이름만 반환해 주세요. 한글로 답변하세요",
    "객체 탐지": "이 이미지에서 발견된 항목들의 목록을 쉼표로 구분하여 한글로 생성해 주세요. 항목 목록만 반환해 주세요.",
    "주요 객체 인식": "이미지에서 주요 객체의 이름을 한글로 지정해 주세요. <object> 태그에 포함된 객체 이름만 반환해 주세요.",
    "이야기 창작": "이 이미지를 바탕으로 허구의 단편 소설을 한글로 작성해 주세요.",
    "질문에 대한 답변": "이 이미지 속 사람들은 어떤 감정을 표현하고 있나요? 한글로 표현해주세요",
    "텍스트 인식": "이 이미지에 있는 텍스트를 전사해 주세요. ",
    "텍스트 번역": "이 이미지의 텍스트를 프랑스어로 번역해 주세요.",
    "기타": "",
}

prompt_options = list(prompt_options_dict)

image_options_dict = {
    "Food": "images/food.jpg",
    "People": "images/people.jpg",
    "Person and cat": "images/person_and_cat.jpg",
    "Room": "images/room.jpg",
    "Text in image": "images/text2.png",
    "Toy": "images/toy_car.jpg",
    "Other": "images/house.jpg",
}

image_options = list(image_options_dict)


with col1:
    st.subheader("Select an Image")
    
    image_selection = st.radio("Image example:", image_options)
    
    if image_selection == 'Other':
        uploaded_file = st.file_uploader("Select an image", type=['png', 'jpg'], label_visibility="collapsed")
    else:
        uploaded_file = None
    
    if uploaded_file and image_selection == 'Other':
        uploaded_image_preview = glib.get_bytesio_from_bytes(uploaded_file.getvalue())
        st.image(uploaded_image_preview)
    else:
        st.image(image_options_dict[image_selection])
    
    
with col2:
    st.subheader("Prompt")
    
    prompt_selection = st.radio("Prompt example:", prompt_options)
    
    prompt_example = prompt_options_dict[prompt_selection]
    
    prompt_text = st.text_area("Prompt",
        value=prompt_example,
        height=100,
        help="What you want to know about the image.",
        label_visibility="collapsed")
    
    go_button = st.button("Go", type="primary")
    
    
with col3:
    st.subheader("Result")

    if go_button:
        with st.spinner("Processing..."):
            
            if uploaded_file:
                image_bytes = uploaded_file.getvalue()
            else:
                image_bytes = glib.get_bytes_from_file(image_options_dict[image_selection])
            
            response = glib.get_response_from_model(
                prompt_content=prompt_text, 
                image_bytes=image_bytes,
            )
        
        st.write(response)

