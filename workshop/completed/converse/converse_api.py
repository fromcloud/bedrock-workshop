import boto3, json

print("\n----Converse API 를 이용한 기본적인 모델 호출----\n")

session = boto3.Session()
bedrock = session.client(service_name='bedrock-runtime', region_name='us-west-2')

message_list = []

initial_message = {
    "role": "user",
    "content": [
        { "text": "안녕하세요?" } 
    ],
}

message_list.append(initial_message)

response = bedrock.converse(
    modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    messages=message_list,
    inferenceConfig={
        "maxTokens": 2000,
        "temperature": 0
    },
)

response_message = response['output']['message']

print(json.dumps(response_message, ensure_ascii=False, indent=4))

#
print("\n----사용자 메시지와 어시스턴트 메시지를 번갈아 표시합니다.----\n")

message_list.append(response_message)
print(json.dumps(message_list, ensure_ascii=False, indent=4))

#
print("\n----요청 메시지에 이미지 포함시켜 요청해 봅니다----\n")

with open("image.webp", "rb") as image_file:
    image_bytes = image_file.read()

image_message = {
    "role": "user",
    "content": [
        { "text": "Image 1:" },
        {
            "image": {
                "format": "webp",
                "source": {
                    "bytes": image_bytes #no base64 encoding required!
                }
            }
        },
        { "text": "이미지에 대해 설명해주세요" }
    ],
}

message_list.append(image_message)

response = bedrock.converse(
    modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    messages=message_list,
    inferenceConfig={
        "maxTokens": 2000,
        "temperature": 0
    },
)

response_message = response['output']['message']
print(json.dumps(response_message, ensure_ascii=False, indent=4))

message_list.append(response_message)


#
print("\n----시스템 프롬프트 메시지 설정----\n")

summary_message = {
    "role": "user",
    "content": [
        { "text": "현재까지 나눈 대화에 대해 요약해줄 수 있나요?" } 
    ],
}

message_list.append(summary_message)

response = bedrock.converse(
    modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    messages=message_list,
    system=[
        { 
            "text": "해적 스타일로 모든 요청에 대해 답변해주세요.",
        }
    ],
    inferenceConfig={
        "maxTokens": 2000,
        "temperature": 0
    },
)

response_message = response['output']['message']
print(json.dumps(response_message, ensure_ascii=False, indent=4))

message_list.append(response_message)

#
print("\n----응답의 메타 데이터와 사용된 토큰 수 정보 얻기----\n")

print("Stop Reason:", response['stopReason'])
print("Usage:", json.dumps(response['usage'], indent=4))

