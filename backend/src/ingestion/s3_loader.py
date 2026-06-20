"""
s3_loader.py — Author: Suresh D R | AI Product Developer & Technology Mentor
Downloads raw documents from S3 and uploads processed results back.
"""
import os, json, boto3
from botocore.exceptions import ClientError

S3_BUCKET  = os.getenv("S3_BUCKET", "insurance-rag-bucket-2026")
AWS_REGION = os.getenv("AWS_REGION", "eu-north-1")

def get_s3():
    return boto3.client("s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=AWS_REGION)

def list_raw_files(prefix="raw/"):
    resp = get_s3().list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)
    return [o["Key"] for o in resp.get("Contents", []) if not o["Key"].endswith("/")]

def download_file(s3_key, local_path):
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    get_s3().download_file(S3_BUCKET, s3_key, local_path)
    return local_path

def upload_file(local_path, s3_key):
    get_s3().upload_file(local_path, S3_BUCKET, s3_key)
    return s3_key

def save_json(data, s3_key):
    get_s3().put_object(Bucket=S3_BUCKET, Key=s3_key,
        Body=json.dumps(data, ensure_ascii=False, indent=2).encode(),
        ContentType="application/json")

def load_json(s3_key):
    obj = get_s3().get_object(Bucket=S3_BUCKET, Key=s3_key)
    return json.loads(obj["Body"].read().decode())

def download_all_raw(local_dir="/tmp/raw"):
    downloaded = []
    for key in list_raw_files("raw/"):
        local = os.path.join(local_dir, key.replace("raw/", "", 1))
        download_file(key, local)
        downloaded.append(local)
        print(f"  Downloaded: {key}")
    return downloaded
