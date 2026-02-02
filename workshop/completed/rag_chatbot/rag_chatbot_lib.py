# 필요한 라이브러리 임포트
import itertools  # 리스트 평탄화(flatten)를 위한 도구
import boto3  # AWS 서비스와 통신하기 위한 SDK
import chromadb  # 벡터 데이터베이스 클라이언트
from chromadb.utils.embedding_functions import AmazonBedrockEmbeddingFunction  # Bedrock 임베딩 함수

# 대화 히스토리에 저장할 최대 메시지 수 (메모리 관리를 위한 제한)
MAX_MESSAGES = 20

class ChatMessage():
    """채팅 메시지를 저장하는 클래스
    
    역할(role)과 텍스트(text)를 포함하여 대화 내용을 구조화
    """
    def __init__(self, role, text):
        """ChatMessage 초기화
        
        Args:
            role (str): 메시지 역할 ('user' 또는 'assistant')
            text (str): 메시지 내용
        """
        self.role = role
        self.text = text

def get_collection(path, collection_name):
    """ChromaDB 컬렉션을 가져오는 함수
    
    벡터 데이터베이스에서 특정 컬렉션을 로드하여 검색에 사용
    
    Args:
        path (str): ChromaDB 데이터베이스 파일 경로
        collection_name (str): 가져올 컬렉션 이름
    
    Returns:
        Collection: ChromaDB 컬렉션 객체
    """
    # AWS 세션 생성
    session = boto3.Session()
    
    # Amazon Bedrock의 Titan 임베딩 모델을 사용하는 임베딩 함수 생성
    embedding_function = AmazonBedrockEmbeddingFunction(
        session=session, 
        region_name='us-west-2',
        model_name="amazon.titan-embed-text-v2:0"
    )
    
    # 영구 저장소에서 ChromaDB 클라이언트 생성
    client = chromadb.PersistentClient(path=path)
    
    # 지정된 컬렉션을 임베딩 함수와 함께 가져오기
    collection = client.get_collection(collection_name, embedding_function=embedding_function)
    
    return collection

def get_vector_search_results(collection, question):
    """벡터 검색을 수행하는 함수
    
    사용자 질문과 유사한 문서를 벡터 데이터베이스에서 검색
    
    Args:
        collection (Collection): ChromaDB 컬렉션 객체
        question (str): 검색할 질문 텍스트
    
    Returns:
        dict: 검색 결과 (documents, distances, metadatas 등 포함)
    """
    # 질문과 가장 유사한 상위 4개의 문서를 검색
    results = collection.query(
        query_texts=[question],  # 검색 쿼리
        n_results=4  # 반환할 결과 개수
    )
    
    return results

def get_tools():
    """Claude 모델이 사용할 수 있는 도구(Tool) 정의
    
    Function Calling을 위한 도구 스펙을 정의하여 모델이 필요시 호출할 수 있도록 함
    
    Returns:
        list: 도구 스펙 리스트
    """
    tools = [
        {
            "toolSpec": {
                # 도구 이름
                "name": "get_amazon_bedrock_information",
                # 도구 설명 (모델이 언제 이 도구를 사용할지 판단하는 기준)
                "description": "Retrieve information about Amazon Bedrock, a managed service for hosting generative AI models.",
                # 입력 스키마 정의
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The retrieval-augmented generation query used to look up information in a repository of FAQs about Amazon Bedrock."
                            }
                        },
                        # 필수 파라미터
                        "required": [
                            "query"
                        ]
                    }
                }
            }
        }
    ]

    return tools

def convert_chat_messages_to_converse_api(chat_messages):
    """ChatMessage 객체 리스트를 Bedrock Converse API 형식으로 변환
    
    내부 ChatMessage 형식을 AWS Bedrock API가 요구하는 형식으로 변환
    
    Args:
        chat_messages (list): ChatMessage 객체 리스트
    
    Returns:
        list: Converse API 형식의 메시지 리스트
    """
    messages = []
    
    # 각 ChatMessage를 Converse API 형식으로 변환
    for chat_msg in chat_messages:
        messages.append({
            "role": chat_msg.role,  # 'user' 또는 'assistant'
            "content": [
                {
                    "text": chat_msg.text  # 메시지 텍스트 내용
                }
            ]
        })
            
    return messages

def process_tool(response_message, messages, bedrock, tool_list):
    """모델의 도구 사용 요청을 처리하는 함수 (RAG 구현의 핵심)
    
    모델이 도구를 호출하면 실제로 벡터 검색을 수행하고 결과를 모델에게 전달
    
    Args:
        response_message (dict): 모델의 응답 메시지
        messages (list): 대화 메시지 리스트
        bedrock: Bedrock 클라이언트
        tool_list (list): 사용 가능한 도구 리스트
    
    Returns:
        tuple: (도구 사용 여부, 최종 응답 텍스트)
    """
    # 모델의 응답을 메시지 히스토리에 추가
    messages.append(response_message)
    
    # 응답 메시지의 콘텐츠 블록들 추출
    response_content_blocks = response_message['content']

    # 도구 실행 결과를 담을 리스트
    follow_up_content_blocks = []
    
    # 각 콘텐츠 블록을 순회하며 도구 사용 요청 확인
    for content_block in response_content_blocks:
        if 'toolUse' in content_block:
            tool_use_block = content_block['toolUse']
            
            # 'get_amazon_bedrock_information' 도구가 호출된 경우
            if tool_use_block['name'] == 'get_amazon_bedrock_information':
                
                # ChromaDB 컬렉션 가져오기
                collection = get_collection("../../data/chroma", "bedrock_faqs_collection")
                
                # 모델이 생성한 검색 쿼리 추출
                query = tool_use_block['input']['query']
                
                print("----QUERY:----")
                print(query)
                
                # 벡터 검색 수행
                search_results = get_vector_search_results(collection, query)
    
                # ChromaDB가 반환하는 중첩 리스트를 평탄화 (flatten)
                flattened_results_list = list(itertools.chain(*search_results['documents']))
                
                # 검색된 문서들을 하나의 문자열로 결합 (RAG 컨텍스트)
                rag_content = "\n\n".join(flattened_results_list)
                
                print("----RAG CONTENT----")
                print(rag_content)
                
                # 도구 실행 결과를 모델에게 전달할 형식으로 구성
                follow_up_content_blocks.append({
                    "toolResult": {
                        "toolUseId": tool_use_block['toolUseId'],  # 도구 호출 ID 매칭
                        "content": [
                            { "text": rag_content }  # 검색된 컨텍스트 전달
                        ]
                    }
                })
                
    # 도구가 실제로 사용된 경우
    if len(follow_up_content_blocks) > 0:
        
        # 도구 실행 결과를 user 역할의 메시지로 추가
        follow_up_message = {
            "role": "user",
            "content": follow_up_content_blocks,
        }
    
        messages.append(follow_up_message)
        
        # RAG 컨텍스트를 포함하여 모델에게 다시 요청
        response = bedrock.converse(
            modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            messages=messages,
            inferenceConfig={
                "maxTokens": 2000,  # 최대 생성 토큰 수
                "temperature": 0,  # 결정적 응답 (낮을수록 일관성 높음)
                "topP": 0.9,  # 누적 확률 샘플링
                "stopSequences": []  # 생성 중단 시퀀스
            },
            toolConfig={
                "tools": tool_list  # 도구 설정 전달
            }
        )
        
        # 도구 사용됨, RAG 기반 응답 반환
        return True, response['output']['message']['content'][0]['text']
        
    else:
        # 도구 사용 안됨, 응답 없음
        return False, None

def chat_with_model(message_history, new_text=None):
    """모델과 대화하는 메인 함수 (RAG 기반 챗봇의 진입점)
    
    사용자 메시지를 받아 모델에게 전달하고, 필요시 RAG를 통해 응답 생성
    
    전체 프로세스:
    1. 사용자 메시지를 히스토리에 추가
    2. 메시지 수 제한 확인 및 오래된 메시지 삭제
    3. 모델에게 첫 번째 요청 전송
    4. 모델이 도구 사용을 요청하면 벡터 검색 수행
    5. 검색 결과를 모델에게 전달하여 최종 응답 생성
    6. 응답을 히스토리에 추가
    
    Args:
        message_history (list): ChatMessage 객체들의 대화 히스토리
        new_text (str): 사용자의 새로운 메시지
    
    Returns:
        None (message_history가 직접 수정됨)
    """
    # AWS 세션 및 Bedrock 클라이언트 생성
    session = boto3.Session()
    bedrock = session.client(service_name='bedrock-runtime', region_name='us-west-2')
    
    # 사용 가능한 도구 리스트 가져오기
    tool_list = get_tools()
    
    # 새로운 사용자 메시지를 ChatMessage 객체로 생성
    new_text_message = ChatMessage('user', text=new_text)
    message_history.append(new_text_message)
    
    # 현재 메시지 수 확인
    number_of_messages = len(message_history)
    
    # 메시지 수가 최대치를 초과하면 오래된 메시지 삭제
    if number_of_messages > MAX_MESSAGES:
        # user와 assistant 메시지를 쌍으로 삭제 (2개씩)
        del message_history[0 : (number_of_messages - MAX_MESSAGES) * 2]
    
    # ChatMessage 형식을 Converse API 형식으로 변환
    messages = convert_chat_messages_to_converse_api(message_history)
    
    # 모델에게 첫 번째 요청 전송
    response = bedrock.converse(
        modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",  # Claude 3.7 Sonnet 모델
        messages=messages,
        inferenceConfig={
            "maxTokens": 2000,  # 최대 생성 토큰 수
            "temperature": 0,  # 결정적 응답 (일관성 우선)
            "topP": 0.9,  # 누적 확률 샘플링
            "stopSequences": []  # 생성 중단 시퀀스 없음
        },
        toolConfig={
            "tools": tool_list  # Function Calling을 위한 도구 설정
        }
    )
    
    # 모델의 응답 메시지 추출
    response_message = response['output']['message']
    
    # 도구 사용 여부 확인 및 처리 (RAG 수행)
    tool_used, output = process_tool(response_message, messages, bedrock, tool_list)
    
    # 도구가 사용되지 않은 경우 원래 응답 사용
    if not tool_used:
        output = response['output']['message']['content'][0]['text']
    
    # 최종 응답 출력
    print("----FINAL RESPONSE----")
    print(output)
    
    # 어시스턴트 응답을 ChatMessage로 생성하여 히스토리에 추가
    response_chat_message = ChatMessage('assistant', output)
    message_history.append(response_chat_message)
    
    return
