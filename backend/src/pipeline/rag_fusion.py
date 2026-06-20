"""
rag_fusion.py — Author: Suresh D R | AI Product Developer & Technology Mentor
Generates query variants and fuses retrieval results for ambiguous questions.
"""
import os, json
from openai import OpenAI
from src.retrieval.hybrid_search import hybrid_search, rrf_merge

PROMPT = """Insurance question: "{question}"
Generate 4 variants targeting: coverage, exclusions, limits, eligibility.
Return as JSON list only."""

def rag_fusion_search(question, top_k=20, tenant_id="star-health"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp   = client.chat.completions.create(
        model="gpt-4o-mini", temperature=0.3,
        messages=[{"role":"user","content":PROMPT.format(question=question)}])
    try:    variants = [question] + json.loads(resp.choices[0].message.content)
    except: variants = [question]
    seen, all_res = set(), []
    for v in variants:
        for c in hybrid_search(v, top_k=10, tenant_id=tenant_id):
            if c["chunk_id"] not in seen:
                seen.add(c["chunk_id"])
                all_res.append(c)
    return all_res[:top_k]
