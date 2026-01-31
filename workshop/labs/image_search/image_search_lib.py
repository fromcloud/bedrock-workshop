import itertools
import boto3
import json
import base64
import chromadb
from io import BytesIO

# Bedrock을 호출하여 이미지, 텍스트 또는 둘 모두에서 벡터를 추출합니다.
def get_multimodal_vector(input_image_base64=None, input_text=None):
    
    session = boto3.Session()

    bedrock = session.client(service_name='bedrock-runtime') #Bedrock 클라이언트를 생성합니다.
    
    request_body = {}
    
    if input_text:
        request_body["inputText"] = input_text
        
    if input_image_base64:
        request_body["inputImage"] = input_image_base64
    
    body = json.dumps(request_body)
    
    response = bedrock.invoke_model(
    	body=body, 
    	modelId="amazon.titan-embed-image-v1", 
    	accept="application/json", 
    	contentType="application/json"
    )
    
    response_body = json.loads(response.get('body').read())
    
    embedding = response_body.get("embedding")
    
    return embedding

# 이전에 생성한 Chroma 벡터 데이터베이스에 액세스하는 함수를 추가합니다.
def get_collection(path, collection_name):

    client = chromadb.PersistentClient(path=path)
    collection = client.get_collection(collection_name)
    
    return collection

# 벡터를 검색합니다. 
def get_vector_search_results(collection, query_embedding):
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=4
    )
    
    return results


# 파일 바이트에서 base64로 인코딩된 문자열을 가져옵니다.
def get_base64_from_bytes(image_bytes):
    
    image_io = BytesIO(image_bytes)
    
    image_base64 = base64.b64encode(image_io.getvalue()).decode("utf-8")
    
    return image_base64


# 지정된 검색어와/또는 검색 이미지를 기반으로 이미지 목록을 가져옵니다.
def get_similarity_search_results(search_term=None, search_image=None):
    
    search_image_base64 = (get_base64_from_bytes(search_image) if search_image else None)

    query_embedding = get_multimodal_vector(input_text=search_term, input_image_base64=search_image_base64)
    
    collection = get_collection("/environment/workshop/data", "image_collection")
    
    search_results = get_vector_search_results(collection, query_embedding)
    
    flattened_results_list = list(itertools.chain(*search_results['documents'])) #flatten the list of lists returned by chromadb
    
    
    results_images = []
    
    for res in flattened_results_list: #load images into list
        
        with open(res, "rb") as f: 
            img = BytesIO(f.read())
        
        results_images.append(img)
    
    
    return results_images