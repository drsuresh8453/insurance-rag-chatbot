"""
reranker.py — Author: Suresh D R | AI Product Developer & Technology Mentor
Reranker disabled — cross-encoder too heavy for t3.small/t3.medium.
Falls back to RRF hybrid search scores directly.
"""

def rerank(query, chunks, top_k=5):
    """Passthrough — returns top_k chunks sorted by existing rrf_score."""
    if not chunks:
        return []
    sorted_chunks = sorted(chunks, key=lambda x: x.get("rrf_score", 0), reverse=True)
    for c in sorted_chunks:
        c["rerank_score"] = round(c.get("rrf_score", 0.5), 4)
    return sorted_chunks[:top_k]
