"""
bulk_load.py — Author: Suresh D R | AI Product Developer & Technology Mentor
One-time bulk load of all S3 documents into ChromaDB.
Run: python -m src.ingestion.bulk_load
"""
import os, pickle
import pandas as pd
from rank_bm25 import BM25Okapi
from src.ingestion.s3_loader   import download_all_raw, save_json, get_s3
from src.ingestion.docx_parser  import parse_docx
from src.ingestion.chunker      import chunk_document
from src.ingestion.embedder     import store_chunks

S3_BUCKET = os.getenv("S3_BUCKET","insurance-rag-bucket-2026")

DOC_META = {
    "star_health_comprehensive_policy.docx": {
        "doc_id":"star-health-comp-2024","plan_name":"Star Comprehensive Individual 2024",
        "insurer":"Star Health","doc_type":"health_policy",
        "tenant_id":"star-health","doc_version":"2024-v1",
    },
    "claims_guidelines.docx": {
        "doc_id":"claims-guidelines-2024","plan_name":"Claims Guidelines",
        "insurer":"Star Health","doc_type":"claims_guidelines",
        "tenant_id":"star-health","doc_version":"3.2",
    },
    "agent_product_manual.docx": {
        "doc_id":"agent-manual-2024","plan_name":"Multi-Plan Agent Manual",
        "insurer":"Star Health/HDFC/Bajaj","doc_type":"product_manual",
        "tenant_id":"star-health","doc_version":"Q1-2024",
    },
}

def run():
    print("Downloading files from S3...")
    download_all_raw("/tmp/raw")
    all_chunks = []

    print("Parsing Word documents...")
    for fname, meta in DOC_META.items():
        path = f"/tmp/raw/star-health/{fname}"
        if not os.path.exists(path):
            print(f"  SKIP: {fname}")
            continue
        paras, tables = parse_docx(path)
        chunks = chunk_document(fname, paras, tables, meta)
        all_chunks.extend(chunks)
        print(f"  {fname}: {len(chunks)} chunks")

    print("Parsing CSV files...")
    for csv_f, doc_id, dtype in [
        ("hospital_network.csv","hospital-network","hospital_data"),
        ("product_comparison.csv","product-comparison","product_comparison"),
    ]:
        path = f"/tmp/raw/data/{csv_f}"
        if not os.path.exists(path): continue
        df = pd.read_csv(path)
        for idx, row in df.iterrows():
            row = row.to_dict()
            if dtype == "hospital_data":
                text = (f"{row['hospital_name']} in {row['city']}. "
                        f"Specializations: {row['specializations']}. "
                        f"Cashless: {row['cashless_plans']}. "
                        f"Pre-auth: {row['pre_auth_time_hours']}h.")
            else:
                text = (f"{row.get('insurer','')} {row.get('plan_name','')} "
                        f"Sum: Rs.{row.get('sum_insured_inr',0):,}. "
                        f"Room rent: Rs.{row.get('room_rent_limit_inr',0):,}/day.")
            all_chunks.append({
                "chunk_id":f"{doc_id}-chunk-{idx+1:04d}","text":text,
                "chunk_type":dtype,"section_name":dtype,"source_file":csv_f,
                "doc_id":doc_id,"plan_name":row.get("plan_name",""),
                "insurer":row.get("insurer",""),"doc_type":dtype,
                "tenant_id":"star-health","doc_version":"2024",
                "char_count":len(text),"word_count":len(text.split()),
            })
        print(f"  {csv_f}: {len(df)} chunks")

    print(f"Total chunks: {len(all_chunks)}")
    print("Embedding and storing in ChromaDB...")
    store_chunks(all_chunks)

    print("Building BM25 index...")
    bm25    = BM25Okapi([c["text"].lower().split() for c in all_chunks])
    bm25_pkl = pickle.dumps({"index":bm25,"corpus":all_chunks})
    s3 = get_s3()
    s3.put_object(Bucket=S3_BUCKET, Key="indexes/bm25_index.pkl", Body=bm25_pkl)

    print("Saving chunks to S3...")
    save_json({"total":len(all_chunks),"chunks":all_chunks},"processed/all_chunks.json")
    print("Bulk load complete.")

if __name__ == "__main__":
    run()
