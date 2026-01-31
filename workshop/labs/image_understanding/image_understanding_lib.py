import boto3
from io import BytesIO


# 파일 및 이미지 처리 헬퍼 함수를 추가합니다.
# 헬퍼 함수는 파일, 이미지 및 바이트 간에 데이터를 변환하는 데 사용됩니다.

# file bytes 로부터 BytesIO 객체를 가져옵니다.
def get_bytesio_from_bytes(image_bytes):
    image_io = BytesIO(image_bytes)
    return image_io

# 디스크의 파일로부터 bytes 를 로드합니다. 
def get_bytes_from_file(file_path):
    with open(file_path, "rb") as image_file:
        file_bytes = image_file.read()
    return file_bytes

# Anthropic Claude를 사용하여 응답 생성
def get_response_from_model(prompt_content, image_bytes, mask_prompt=None):
    session = boto3.Session()
    
    bedrock = session.client(service_name='bedrock-runtime') #Bedrock 클라이언트를 생성합니다.
    
    image_message = {
        "role": "user",
        "content": [
            { "text": "Image 1:" },
            {
                "image": {
                    "format": "jpeg", 
                    "source": {
                        "bytes": image_bytes 
                    }
                }
            },
            { "text": prompt_content }
        ],
    }
    
    response = bedrock.converse(
        modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        messages=[image_message],
        inferenceConfig={
            "maxTokens": 2000,
            "temperature": 0
        },
    )
    
    output = response['output']['message']['content'][0]['text']
    
    return output

