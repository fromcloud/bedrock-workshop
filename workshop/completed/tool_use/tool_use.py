import boto3, json, math

print("\n---- 1) tool 정의 및 Claude 가 tool 사용에 대해 요청하도록 메시지 보내기----\n")

session = boto3.Session()
bedrock = session.client(service_name='bedrock-runtime', region_name='us-west-2')

tool_list = [
    {
        "toolSpec": {
            "name": "cosine",
            "description": "X 의 코사인값을 계산합니다.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "x": {
                            "type": "number",
                            "description": "함수에 전달한 수"
                        }
                    },
                    "required": ["x"]
                }
            }
        }
    }
]

message_list = []

initial_message = {
    "role": "user",
    "content": [
        { "text": "7의 코사인 값은 얼마인가요?" } 
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
    toolConfig={
        "tools": tool_list
    },
    system=[{"text":"당신은 tool 을 사용해서 수학계산을 해야합니다."}]
)

response_message = response['output']['message']
print(json.dumps(response_message, ensure_ascii=False, indent=4))
message_list.append(response_message)


# print("\n----toolUse 컨텐츠 블록 기반 함수 호출----\n")

response_content_blocks = response_message['content']

for content_block in response_content_blocks:
    if 'toolUse' in content_block:
        tool_use_block = content_block['toolUse']
        tool_use_name = tool_use_block['name']
        
        print(f"Using tool {tool_use_name}")
        
        if tool_use_name == 'cosine':
            tool_result_value = math.cos(tool_use_block['input']['x'])
            print(tool_result_value)
            
    elif 'text' in content_block:
        print(content_block['text'])


print("\n---- 2) tool 의 결과를 Claude 모델에게 전달----\n")

follow_up_content_blocks = []

for content_block in response_content_blocks:
    if 'toolUse' in content_block:
        tool_use_block = content_block['toolUse']
        tool_use_name = tool_use_block['name']
        
        
        if tool_use_name == 'cosine':
            tool_result_value = math.cos(tool_use_block['input']['x'])
            
            follow_up_content_blocks.append({
                "toolResult": {
                    "toolUseId": tool_use_block['toolUseId'],
                    "content": [
                        {
                            "json": {
                                "result": tool_result_value
                            }
                        }
                    ]
                }
            })

if len(follow_up_content_blocks) > 0:
    
    follow_up_message = {
        "role": "user",
        "content": follow_up_content_blocks,
    }
    
    message_list.append(follow_up_message)

    response = bedrock.converse(
        modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        messages=message_list,
        inferenceConfig={
            "maxTokens": 2000,
            "temperature": 0
        },
        toolConfig={
            "tools": tool_list
        },
        system=[{"text":"당신은 tool 을 사용해서 수학계산을 해야합니다."}]
    )
    
    response_message = response['output']['message']
    
    message_list.append(response_message)
    print(json.dumps(message_list, ensure_ascii=False, indent=4))


print("\n---- 참고) Error handling - tool 사용 실패에 대해 Claude 에게 알리기----\n")

del message_list[-2:] #Remove the last request and response messages

content_block = next((block for block in response_content_blocks if 'toolUse' in block), None)

if content_block:
    tool_use_block = content_block['toolUse']
    
    error_tool_result = {
        "toolResult": {
            "toolUseId": tool_use_block['toolUseId'],
            "content": [
                {
                    "text": "invalid function: cosine"
                }
            ],
            "status": "error"
        }
    }
    
    follow_up_message = {
        "role": "user",
        "content": [error_tool_result],
    }
    
    message_list.append(follow_up_message)
    
    response = bedrock.converse(
        modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        messages=message_list,
        inferenceConfig={
            "maxTokens": 2000,
            "temperature": 0
        },
        toolConfig={
            "tools": tool_list
        },
        system=[{"text":"당신은 tool 을 사용해서 수학계산을 해야합니다."}]
    )
    
    response_message = response['output']['message']
    print(json.dumps(response_message, ensure_ascii=False,  indent=4))
    message_list.append(response_message)

