"""
hybrid_search.py — Author: Suresh D R | AI Product Developer & Technology Mentor
Combines vector search and BM25 using Reciprocal Rank Fusion.
"""
from src.ingestion.embedder import embed_query, vector_search
from src.retrieval.bm25_search import bm25_search

def rrf_merge(l1, l2, k=60):
    scores = {}
    for rank, doc in enumerate(l1, 1):
        did = doc["chunk_id"]
        scores.setdefault(did, {"doc":doc,"score":0})["score"] += 1/(k+rank)
    for rank, doc in enumerate(l2, 1):
        did = doc["chunk_id"]
        scores.setdefault(did, {"doc":doc,"score":0})["score"] += 1/(k+rank)
    sorted_r = sorted(scores.values(), key=lambda x:x["score"], reverse=True)
    for item in sorted_r:
        item["doc"]["rrf_score"] = round(item["score"],6)
    return [item["doc"] for item in sorted_r]

def hybrid_search(query, top_k=20, tenant_id="star-health", ctype=None):
    q_emb   = embed_query(query)
    v_res   = vector_search(q_emb, n=top_k*2, ctype=ctype, tenant_id=tenant_id)
    b_res   = bm25_search(query, top_k=top_k*2)
    return rrf_merge(v_res, b_res)[:top_k]
