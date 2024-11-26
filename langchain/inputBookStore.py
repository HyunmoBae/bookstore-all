import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from pymongo import MongoClient
import os

# CSV 파일 로드
df = pd.read_csv('bookstore.csv')  # 파일 이름을 적절히 변경하세요

# 텍스트 데이터 준비
df['text'] = df['atmosphere'].fillna('')

# TF-IDF 벡터화
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df['text'])

# DocumentDB 연결 설정
username = os.environ.get("DB_USERNAME")
password = os.environ.get("DB_PASSWORD")
host = os.environ.get("DB_HOST")
port = 27017
ca_file_path = "global-bundle.pem"

connection_string = f"mongodb://{username}:{password}@{host}:{port}/?tls=true&tlsCAFile={ca_file_path}&retryWrites=false"

client = MongoClient(connection_string, tlsCAFile=ca_file_path)
db = client["bookstore"]
collection = db["bookstore"]  # 새로운 컬렉션 이름

# 데이터와 임베딩을 DocumentDB에 저장
for i, row in df.iterrows():
    embedding = tfidf_matrix[i].toarray()[0].tolist()
    document = {
        "id": row['id'],
        "atmosphere": row['atmosphere'],
        "embedding": embedding
    }
    collection.insert_one(document)

print("데이터가 성공적으로 임베딩되어 DocumentDB에 저장되었습니다.")

# 연결 종료

client.close()
