"""
bm25_search.py — Author: Suresh D R | AI Product Developer & Technology Mentor
BM25 keyword search over all chunks.
"""
import os, pickle, boto3
from rank_bm25 import BM25Okapi

_bm25  = None
_corpus = None

def _load():
    global _bm25, _corpus
    if _bm25: return
    s3_key = "indexes/bm25_index.pkl"
    s3 = boto3.client("s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION","eu-north-1"))
    obj = s3.get_object(Bucket=os.getenv("S3_BUCKET","insurance-rag-bucket-2026"), Key=s3_key)
    data = pickle.loads(obj["Body"].read())
    _bm25   = data["index"]
    _corpus = data["corpus"]

def bm25_search(query, top_k=20):
    _load()
    scores  = _bm25.get_scores(query.lower().split())
    top_idx = scores.argsort()[::-1][:top_k]
    results = []
    for idx in top_idx:
        if scores[idx] > 0:
            c = dict(_corpus[idx])
            c["bm25_score"] = round(float(scores[idx]),4)
            results.append(c)
    return results
