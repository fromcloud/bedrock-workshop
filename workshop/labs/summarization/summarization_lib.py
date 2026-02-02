import boto3

# 문서 바이트와 프롬프트를 Amazon Bedrock에 전달한 다음 응답 텍스트를 반환합니다.
def get_summary(input_text):
    
    with open("amazon-leadership-principles-070621-us.pdf", "rb") as doc_file:
        doc_bytes = doc_file.read()

    doc_message = {
        "role": "user",
        "content": [
            {
                "document": {
                    "name": "Document 1",
                    "format": "pdf",
                    "source": {
                        "bytes": doc_bytes
                    }
                }
            },
            { "text": input_text }
        ]
    }
    
    session = boto3.Session()
    bedrock = session.client(service_name='bedrock-runtime', region_name='us-west-2')
    
    response = bedrock.converse(
        modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        messages=[doc_message],
        inferenceConfig={
            "maxTokens": 2000,
            "temperature": 0
        },
    )
    
    return response['output']['message']['content'][0]['text']

