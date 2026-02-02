import streamlit as st
import image_understanding_lib as glib

st.set_page_config(layout="wide", page_title="Image Understanding")

st.title("Image Understanding")

col1, col2, col3 = st.columns(3)

prompt_options_dict = {
    "Image caption": "이 이미지에 대한 간단한 설명을 한글로 제공해 주세요.",
    "Detailed description": "이 이미지에 대해 매우 자세한 설명을  한글로 제공해 주십시오..",
    "Image classification": "이 이미지를 다음 카테고리 중 하나로 분류해 주세요: 사람, 음식, 기타. 카테고리 이름만 반환해 주세요.",
    "Object recognition": "이 이미지에 있는 항목들을 쉼표로 구분된 목록으로 만들어 주세요. 항목 목록만 반환해 주세요.  한글로 처리해주세요.",
    "Subject identification": "이미지에서 가장 중요한 객체의 이름을 알려주세요. 객체의 이름은 <object> 태그 안에만 넣어서 입력해 주세요.",
    "Writing a story": "이 이미지를 바탕으로 허구적인 단편 소설을  한글로 써 주세요.",
    "Answering questions": "이 사진 속 사람들은 어떤 감정을 표현하고 있나요?  한글로 설명해주세요",
    "Transcribing text": "이 이미지에 있는 텍스트를 모두 옮겨 적어주세요.",
    "Translating text": "이 이미지의 텍스트를 프랑스어로 번역해 주세요.",
    "Other": "",
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
