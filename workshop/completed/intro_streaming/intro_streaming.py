import boto3

def chunk_handler(chunk):
    print(chunk, end='')


def get_streaming_response(prompt, streaming_callback):
    
    session = boto3.Session()
    bedrock = session.client(service_name='bedrock-runtime', region_name='us-west-2')
    
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
    
    stream = response.get('stream')
    for event in stream:
        if "contentBlockDelta" in event:
            streaming_callback(event['contentBlockDelta']['delta']['text'])


prompt = "강아지 두 마리와 고양이 두 마리가 절친한 친구가 된 이야기를 들려주세요.:"
                
get_streaming_response(prompt, chunk_handler)
print("\n")
