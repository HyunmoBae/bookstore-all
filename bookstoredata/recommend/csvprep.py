import csv
import json
import os
import shutil
import boto3
from botocore.exceptions import NoCredentialsError

def read_metadata_definition(metadata_file):
    with open(metadata_file, 'r') as f:
        return json.load(f)

def process_csv(input_csv, metadata_definition, output_dir):
    embedding_attributes = metadata_definition['csv']['embeddingattributes']
    metadata_attributes = metadata_definition['csv']['metadataattributes']
    index_id_attributes = metadata_definition['csv']['index_id']

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    processed_files = []

    with open(input_csv, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            index_id = row[index_id_attributes[0]]  # Assuming ESNTL_ID is the index

            # Process embedding attributes
            embedding_data = {attr: row[attr] for attr in embedding_attributes}
            embedding_output_path = os.path.join(output_dir, f'{index_id}.csv')
            with open(embedding_output_path, 'w', newline='', encoding='utf-8') as embedding_csv:
                csv_writer = csv.DictWriter(embedding_csv, fieldnames=embedding_attributes)
                csv_writer.writeheader()
                csv_writer.writerow(embedding_data)

            # Process metadata attributes
            metadata_data = {attr: row[attr] for attr in metadata_attributes}
            metadata_output_path = f'{embedding_output_path}.metadata.json'
            with open(metadata_output_path, 'w', encoding='utf-8') as metadata_json:
                json.dump({'metadataAttributes': metadata_data}, metadata_json, indent=4, ensure_ascii=False)

            processed_files.extend([embedding_output_path, metadata_output_path])

    print(f"Files generated in: {output_dir}")
    return processed_files

def upload_to_s3(files, bucket_name, region_name):
    s3 = boto3.client('s3', region_name=region_name)
    
    for file in files:
        file_name = os.path.basename(file)
        try:
            s3.upload_file(file, bucket_name, file_name)
            print(f"Successfully uploaded {file_name} to {bucket_name} in region {region_name}")
        except NoCredentialsError:
            print("Credentials not available")
            return False
        except Exception as e:
            print(f"An error occurred while uploading {file_name}: {str(e)}")
            return False
    
    return True

def main():
    input_csv = '../csv/bookstore.csv'
    metadata_file = '../metadata/metadata_definition.json'
    output_dir = r'C:\projects\bookstore\bookstoredata\csv'
    s3_bucket_name = 'bookstore-test-bucket'  # 여기에 실제 S3 버킷 이름을 입력하세요
    region_name = 'ap-northeast-1'  # 여기에 원하는 리전 이름을 입력하세요 (예: 서울 리전)

    metadata_definition = read_metadata_definition(metadata_file)
    print("Metadata Definition:")
    print(json.dumps(metadata_definition, indent=2))

    print("Processing CSV...")
    processed_files = process_csv(input_csv, metadata_definition, output_dir)

    print("Uploading files to S3...")
    if upload_to_s3(processed_files, s3_bucket_name, region_name):
        print(f"All files successfully uploaded to S3 in region {region_name}")
    else:
        print("Failed to upload some or all files to S3")

if __name__ == '__main__':
    main()
