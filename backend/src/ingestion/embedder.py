"""
embedder.py — Author: Suresh D R | AI Product Developer & Technology Mentor
Generates OpenAI embeddings and stores chunks in ChromaDB.
"""
import os, time
import chromadb
from openai import OpenAI

EMBED_MODEL = "text-embedding-3-large"
CHROMA_PATH = os.getenv("CHROMA_PATH", "/tmp/chromadb")
COLLECTION  = "insurance_policies"
_oai = None
_col = None

def get_openai():
    global _oai
    if not _oai: _oai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _oai

def get_collection():
    global _col
    if not _col:
        c = chromadb.PersistentClient(path=CHROMA_PATH)
        try:    _col = c.get_collection(COLLECTION)
        except: _col = c.create_collection(COLLECTION, metadata={"hnsw:space":"cosine"})
    return _col

def embed_texts(texts, batch_size=50):
    all_emb = []
    for i in range(0, len(texts), batch_size):
        resp = get_openai().embeddings.create(input=texts[i:i+batch_size], model=EMBED_MODEL)
        all_emb.extend([e.embedding for e in resp.data])
        time.sleep(0.3)
    return all_emb

def embed_query(question):
    resp = get_openai().embeddings.create(input=[question], model=EMBED_MODEL)
    return resp.data[0].embedding

def store_chunks(chunks):
    col  = get_collection()
    texts = [c["text"] for c in chunks]
    ids   = [c["chunk_id"] for c in chunks]
    metas = [{
        "chunk_type":   c.get("chunk_type","general")[:50],
        "section_name": c.get("section_name","")[:100],
        "plan_name":    c.get("plan_name","")[:100],
        "insurer":      c.get("insurer","")[:50],
        "doc_type":     c.get("doc_type","")[:50],
        "doc_id":       c.get("doc_id","")[:100],
        "tenant_id":    c.get("tenant_id","star-health"),
        "source_file":  c.get("source_file","")[:100],
    } for c in chunks]
    embeddings = embed_texts(texts)
    col.add(documents=texts, embeddings=embeddings, metadatas=metas, ids=ids)
    return len(chunks)

def vector_search(query_emb, n=20, ctype=None, tenant_id="star-health"):
    col   = get_collection()
    where = {"$and":[{"tenant_id":tenant_id},{"chunk_type":ctype}]} if ctype else {"tenant_id":tenant_id}
    res   = col.query(query_embeddings=[query_emb], n_results=n, where=where)
    return [{
        "chunk_id":    res["ids"][0][i],
        "text":        res["documents"][0][i],
        "chunk_type":  res["metadatas"][0][i]["chunk_type"],
        "section_name":res["metadatas"][0][i]["section_name"],
        "plan_name":   res["metadatas"][0][i]["plan_name"],
        "similarity":  round(1-res["distances"][0][i],4),
    } for i in range(len(res["ids"][0]))]
