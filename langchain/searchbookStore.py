from pymongo import MongoClient
import numpy as np
from scipy.spatial.distance import cosine
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
import os

# 환경 변수에서 값 가져오기
api_key = os.environ.get("GOOGLE_API_KEY")
db_username = os.environ.get("DB_USERNAME")
db_password = os.environ.get("DB_PASSWORD")
db_host = os.environ.get("DB_HOST")

# 환경 변수가 설정되어 있는지 확인
if not all([api_key, db_username, db_password, db_host]):
    raise ValueError("필요한 환경 변수가 설정되지 않았습니다.")

# Gemini API 키 설정
genai.configure(api_key=api_key)

# DocumentDB 연결 설정
port = 27017
ca_file_path = "global-bundle.pem"
connection_string = f"mongodb://{db_username}:{db_password}@{db_host}:{port}/?tls=true&tlsCAFile={ca_file_path}&retryWrites=false"

# MongoDB(DocumentDB) 연결
client = MongoClient(connection_string, tlsCAFile=ca_file_path)
db = client["bookstore"]
collection = db["bookstore"]

# Gemini 임베딩 모델 초기화
embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

def similarity_search(query, k=3):
    # 쿼리 텍스트를 임베딩 벡터로 변환
    query_embedding = embeddings_model.embed_query(query)

    # 모든 문서와 임베딩 가져오기
    all_docs = list(collection.find({}))

    # 코사인 유사도 계산
    similarities = []
    for doc in all_docs:
        # 문서의 임베딩 벡터 확인 및 필요시 재임베딩
        if 'embedding' not in doc or len(doc['embedding']) != len(query_embedding):
            doc_text = doc['atmosphere']
            doc_embedding = embeddings_model.embed_query(doc_text)
            # 임베딩 업데이트 (선택적)
            # collection.update_one({'_id': doc['_id']}, {'$set': {'embedding': doc_embedding}})
        else:
            doc_embedding = doc['embedding']

        # NumPy 배열로 변환
        query_embedding_np = np.array(query_embedding)
        doc_embedding_np = np.array(doc_embedding)

        similarity = 1 - cosine(query_embedding_np, doc_embedding_np)
        similarities.append((doc, similarity))

    # 유사도에 따라 정렬
    similarities.sort(key=lambda x: x[1], reverse=True)

    # 상위 k개 결과 반환
    return similarities[:k]

# 검색 실행 및 결과 출력
query = "디저트가 맛있는 분위기"
results = similarity_search(query)

for doc, similarity in results:
    print(f"ID: {doc['id']}")
    print(f"Atmosphere: {doc['atmosphere']}")
    print(f"Similarity: {similarity:.4f}")
    print("---")

# 연결 종료
client.close()
