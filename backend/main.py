from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import time
import subprocess
import os
import boto3

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/download-xlsx/")
async def download_xlsx():
    print("Generating and uploading the file...")
    start_time = time.time()
    
    # Generate presigned URL in Python
    s3_client = boto3.client('s3', endpoint_url='http://localhost:4566', aws_access_key_id='test', aws_secret_access_key='test', region_name='us-east-1')
    bucket = "local-bucket"
    key = "output.xlsx"
    
    try:
        s3_client.create_bucket(Bucket=bucket)
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        pass
    
    presigned_url = s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': key}, ExpiresIn=900)
    print(presigned_url)
    
    go_binary_path = os.path.join(os.getcwd(), "main.exe")
    
    subprocess.run([go_binary_path, presigned_url], capture_output=True, text=True, encoding='utf-8', errors='ignore')
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken to generate and upload the file: {elapsed_time} seconds")
    
    return RedirectResponse(url=presigned_url)
