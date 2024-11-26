import csv
import chardet
import codecs
import os

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    return chardet.detect(raw_data)['encoding']

def decode_csv(input_file, output_file):
    # 파일의 인코딩 탐지
    detected_encoding = detect_encoding(input_file)
    print(f"Detected encoding: {detected_encoding}")

    # CSV 파일 읽기
    with codecs.open(input_file, 'r', encoding=detected_encoding, errors='replace') as file_in:
        reader = csv.reader(file_in)
        data = list(reader)

    # UTF-8로 인코딩하여 새 CSV 파일 쓰기
    with codecs.open(output_file, 'w', encoding='utf-8') as file_out:
        writer = csv.writer(file_out)
        writer.writerows(data)

    print(f"Decoded and saved to {output_file}")

# 파일 경로 설정
input_file = r'C:\projects\bookstore\bookstoredata\bookstore.csv'
output_dir = os.path.dirname(input_file)
output_file = os.path.join(output_dir, 'bookstore.csv')

# 디코딩 실행
decode_csv(input_file, output_file)