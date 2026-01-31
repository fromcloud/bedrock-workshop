import itertools
import boto3
import chromadb
from chromadb.utils.embedding_functions import AmazonBedrockEmbeddingFunction

# MAX_MESSAGES는 메모리에 보관되는 이전 채팅 메시지의 상한선을 설정합니다
MAX_MESSAGES = 20

# ChatMessage 클래스는 텍스트 메시지를 저장하는 데 사용됩니다.
class ChatMessage(): #create a class that can store image and text messages
    def __init__(self, role, text):
        self.role = role
        self.text = text

# 생성한 Chroma 벡터 데이터베이스에 액세스
def get_collection(path, collection_name):
    session = boto3.Session()
    embedding_function = AmazonBedrockEmbeddingFunction(session=session, model_name="amazon.titan-embed-text-v2:0")
    
    client = chromadb.PersistentClient(path=path)
    collection = client.get_collection(collection_name, embedding_function=embedding_function)
    
    return collection

# 벡터 저장소에서 결과를 검색하는 함수를 추가합니다.
def get_vector_search_results(collection, question):
    
    results = collection.query(
        query_texts=[question],
        n_results=4
    )
    
    return results

# 생성된 JSON의 형식을 정의하는 데 사용할 도구 정의를 생성하는 함수를 추가합니다.
def get_tools():
    tools = [
        {
            "toolSpec": {
                "name": "get_amazon_bedrock_information",
                "description": "생성형 AI 모델 호스팅을 위한 관리형 서비스인 Amazon Bedrock에 대한 정보를 검색합니다.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Amazon Bedrock에 대한 FAQ 저장소에서 정보를 조회하는 데 사용되는 검색 증강 생성 쿼리입니다."
                            }
                        },
                        "required": [
                            "query"
                        ]
                    }
                }
            }
        }
    ]

    return tools

# ChatMessages를 Converse API 형식으로 변환하는 함수를 추가합니다.
def convert_chat_messages_to_converse_api(chat_messages):
    messages = []
    
    for chat_msg in chat_messages:
        messages.append({
            "role": chat_msg.role,
            "content": [
                {
                    "text": chat_msg.text
                }
            ]
        })
            
    return messages

# 도구 사용 요청을 처리하는 함수를 추가합니다.
def process_tool(response_message, messages, bedrock, tool_list):
    
    messages.append(response_message)
    
    response_content_blocks = response_message['content']

    follow_up_content_blocks = []
    
    for content_block in response_content_blocks:
        if 'toolUse' in content_block:
            tool_use_block = content_block['toolUse']
            
            if tool_use_block['name'] == 'get_amazon_bedrock_information':
                
                collection = get_collection("../../data/chroma", "bedrock_faqs_collection")
                
                query = tool_use_block['input']['query']
                
                print("----QUERY:----")
                print(query)
                
                search_results = get_vector_search_results(collection, query)
    
                flattened_results_list = list(itertools.chain(*search_results['documents'])) #flatten the list of lists returned by chromadb
                
                rag_content = "\n\n".join(flattened_results_list)
                
                print("----RAG CONTENT----")
                print(rag_content)
                
                follow_up_content_blocks.append({
                    "toolResult": {
                        "toolUseId": tool_use_block['toolUseId'],
                        "content": [
                            { "text": rag_content }
                        ]
                    }
                })
                
                
    if len(follow_up_content_blocks) > 0:
        
        follow_up_message = {
            "role": "user",
            "content": follow_up_content_blocks,
        }
    
        messages.append(follow_up_message)
        
        response = bedrock.converse(
            modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            messages=messages,
            inferenceConfig={
                "maxTokens": 2000,
                "temperature": 0,
                "topP": 0.9,
                "stopSequences": []
            },
            toolConfig={
                "tools": tool_list
            }
        )
        
    
        return True, response['output']['message']['content'][0]['text'] #tool used, response
        
    else:
        return False, None #tool not used, no response


# Streamlit 프론트엔드 애플리케이션의 요청을 처리하는 이 함수를 추가합니다.
def chat_with_model(message_history, new_text=None):
    session = boto3.Session()
    bedrock = session.client(service_name='bedrock-runtime') #creates a Bedrock client
    
    tool_list = get_tools()
    
    new_text_message = ChatMessage('user', text=new_text)
    message_history.append(new_text_message)
    
    number_of_messages = len(message_history)
    
    if number_of_messages > MAX_MESSAGES:
        del message_history[0 : (number_of_messages - MAX_MESSAGES) * 2] #make sure we remove both the user and assistant responses
    
    messages = convert_chat_messages_to_converse_api(message_history)
    
    response = bedrock.converse(
        modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        messages=messages,
        inferenceConfig={
            "maxTokens": 2000,
            "temperature": 0,
            "topP": 0.9,
            "stopSequences": []
        },
        toolConfig={
            "tools": tool_list
        }
    )
    
    response_message = response['output']['message']
    
    tool_used, output = process_tool(response_message, messages, bedrock, tool_list)
    
    if not tool_used: #just use the original non-RAG result if no tool was needed
        output = response['output']['message']['content'][0]['text']
    
    
    print("----FINAL RESPONSE----")
    print(output)
    
    response_chat_message = ChatMessage('assistant', output)
    
    message_history.append(response_chat_message)
    
    return



