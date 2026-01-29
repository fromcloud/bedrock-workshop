import boto3, json

print("\n----A basic call to the Converse API----\n")

session = boto3.Session()
bedrock = session.client(service_name='bedrock-runtime')

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
print("\n----Alternating user and assistant messages----\n")

message_list.append(response_message)
print(json.dumps(message_list, ensure_ascii=False, indent=4))

