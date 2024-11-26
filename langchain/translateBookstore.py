import csv
import pandas as pd

# 입력 파일과 출력 파일 경로 설정
input_file = 'bookstore.txt'
output_file = 'bookstore.csv'

# 데이터를 저장할 리스트 초기화
data = []

# txt 파일 읽기
with open(input_file, 'r', encoding='utf-8') as file:
    # 첫 번째 줄은 헤더로 처리
    headers = file.readline().strip().split('\t')
    
    # 나머지 줄 처리
    for line in file:
        values = line.strip().split('\t')
        data.append(values)

# pandas DataFrame으로 변환
df = pd.DataFrame(data, columns=headers)

# CSV 파일로 저장
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"데이터가 {output_file}로 성공적으로 변환되었습니다.")

# 변환된 데이터 확인
print(df.head())
print(f"총 {len(df)} 개의 행이 변환되었습니다.")