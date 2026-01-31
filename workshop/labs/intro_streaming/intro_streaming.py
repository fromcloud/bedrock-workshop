import boto3

def chunk_handler(chunk):
    # end='': 줄바꿈 없이 연속으로 출력
    print(chunk, end='')

def get_streaming_response(prompt, streaming_callback):
    
    session = boto3.Session()
    bedrock = session.client(service_name='bedrock-runtime')
    
    message = {
        "role": "user",
        "content": [ { "text": prompt } ]
    }
    
    response = bedrock.converse_stream(
        modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        messages=[message],
        inferenceConfig={
            "maxTokens": 2000,
            "temperature": 0.0
        }
    )
    
    # stream: 응답 객체에서 스트림을 추출
    # 이벤트 루프: 스트림에서 각 이벤트를 순차적으로 처리
    # contentBlockDelta: 모델이 생성하는 텍스트의 증분(delta) 부분을 포함하는 이벤트
    # streaming_callback: 생성된 텍스트 조각을 실시간으로 처리하는 콜백 함수

    stream = response.get('stream')
    for event in stream:
        if "contentBlockDelta" in event:
            streaming_callback(event['contentBlockDelta']['delta']['text'])

prompt = "강아지 두 마리와 고양이 두 마리가 절친한 친구가 된 이야기를 들려주세요."
                
get_streaming_response(prompt, chunk_handler)
print("\n")

