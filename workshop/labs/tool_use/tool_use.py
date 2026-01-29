import boto3, json, math

print("\n----도구를 정의하고 클로드가 도구 사용을 요청하도록 유도하는 메시지를 보냅니다.----\n")

session = boto3.Session()
bedrock = session.client(service_name='bedrock-runtime')

# 도구 정의 
# name: 도구 이름
# description: 도구의 용도 (모델이 언제 사용할지 판단)
# inputSchema: 도구가 받을 파라미터 정의

tool_list = [
    {
        "toolSpec": {
            "name": "cosine",
            "description": "x 의 cosine 값을 계산합니다.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "x": {
                            "type": "number",
                            "description": "함수에 전달될 변수"
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
        { "text": "7의 cosine 값은 ?" } 
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
    system=[{"text":"수학 계산은 반드시 도구를 사용해서 해야 합니다."}]
)

# 모델의 판단:
# 시스템 프롬프트에서 "수학 계산은 반드시 도구를 사용"이라고 명시
# 사용 가능한 도구 중 cosine 도구가 적합함을 인식
# 직접 답변하지 않고 도구 사용 요청을 반환

response_message = response['output']['message']
print(json.dumps(response_message, ensure_ascii=False, indent=4))
message_list.append(response_message)


print("\n----toolUse 콘텐츠 블록을 기반으로 함수를 호출합니다.----\n")
# 애플리케이션: 모델의 toolUse 요청을 파싱
# 도구 실행: Python의 math.cos(7) 호출
# 결과 획득: 0.7539022543433046

response_content_blocks = response_message['content']

for content_block in response_content_blocks:
    if 'toolUse' in content_block:
        tool_use_block = content_block['toolUse']
        tool_use_name = tool_use_block['name']
        
        print(f"{tool_use_name} 사용")
        
        if tool_use_name == 'cosine':
            tool_result_value = math.cos(tool_use_block['input']['x'])
            print(tool_result_value)
            
    elif 'text' in content_block:
        print(content_block['text'])

print("\n----결과를 다시 모델에게 전달하기----\n")

follow_up_content_blocks = []

for content_block in response_content_blocks:
    if 'toolUse' in content_block:
        tool_use_block = content_block['toolUse']
        tool_use_name = tool_use_block['name']
        
        # 애플리케이션 → 모델: 도구 실행 결과를 toolResult로 전달
        # 역할: "user" (도구 결과는 항상 user 역할로 전달)
        # toolUseId: 어떤 도구 요청에 대한 응답인지 매칭

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
    
    # follow_up_message 에 애플리케이션이 계산한 값이 들어가 있고 그 값을 다시 모델에 전달 
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
        system=[{"text":"수학 계산은 반드시 도구를 사용해서 해야 합니다."}]
    )
    
    response_message = response['output']['message']
    
    message_list.append(response_message)
    print(json.dumps(message_list, ensure_ascii=False, indent=4))

print("\n----에러 처리 : 애플리케이션이 도구 사용에 실패했음을 모델에게 알리기----\n")

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
    
    # 이제 모델은 애플리케이션이 도구 실행에 실패한 것을 알고 자체적으로 문제를 해결하려고 시도함
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
        system=[{"text":"수학 계산은 반드시 도구를 사용해서 해야 합니다."}]
    )
    
    response_message = response['output']['message']
    print(json.dumps(response_message, ensure_ascii=False, indent=4))
    message_list.append(response_message)
