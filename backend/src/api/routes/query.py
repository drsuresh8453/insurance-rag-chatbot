"""
query.py — Author: Suresh D R | AI Product Developer & Technology Mentor
POST /query — Full 9-step RAG pipeline endpoint.
"""
import time
from fastapi import APIRouter, HTTPException
from src.api.schemas import QueryRequest, QueryResponse, SourceItem
from src.guardrails.input_guard  import check_input
from src.guardrails.output_guard import check_output
from src.pipeline.classifier     import classify
from src.pipeline.decomposer     import decompose
from src.pipeline.rag_fusion     import rag_fusion_search
from src.pipeline.generator      import generate_answer, generate_suggestions
from src.pipeline.hallucination  import check_hallucination
from src.pipeline.confidence     import compute_confidence
from src.retrieval.hybrid_search import hybrid_search
from src.retrieval.reranker      import rerank
from src.ingestion.embedder      import embed_query, vector_search

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_endpoint(req: QueryRequest):
    start = time.time()
    question  = req.question.strip()
    tenant_id = req.tenant_id

    # 1. Input guardrails
    is_safe, reason, msg = check_input(question)
    if not is_safe:
        raise HTTPException(status_code=400, detail={"reason": reason, "message": msg})

    # 2. Classify
    qtype = classify(question)

    # 3. Retrieve
    if qtype == "multi_hop":
        sub_qs = decompose(question)
        seen, chunks = set(), []
        for sq in sub_qs:
            for c in hybrid_search(sq, top_k=10, tenant_id=tenant_id):
                if c["chunk_id"] not in seen:
                    seen.add(c["chunk_id"])
                    chunks.append(c)
    elif qtype in ["factual","eligibility","calculation"]:
        chunks = rag_fusion_search(question, top_k=20, tenant_id=tenant_id)
    elif qtype == "negation":
        q_emb  = embed_query(question)
        chunks = vector_search(q_emb, n=20, ctype="exclusion", tenant_id=tenant_id)
        if not chunks: chunks = hybrid_search(question, top_k=20, tenant_id=tenant_id)
    else:
        chunks = hybrid_search(question, top_k=20, tenant_id=tenant_id)

    # 4. Rerank
    top_chunks = rerank(question, chunks, top_k=5)

    # 5–6. Generate
    answer = generate_answer(question, top_chunks, qtype)

    # 7. Hallucination check
    is_grounded, verdict, _ = check_hallucination(answer, top_chunks)

    # 8. Confidence score
    sims    = [c.get("similarity", 0.5) for c in top_chunks]
    reranks = [c.get("rerank_score", 0)  for c in top_chunks]
    conf    = compute_confidence(sims, reranks, is_grounded, qtype)

    # 9. Output guardrails
    answer, _ = check_output(answer, qtype, is_grounded)

    # Suggestions
    suggestions = generate_suggestions(question)

    return QueryResponse(
        question=question,
        answer=answer,
        confidence_score=conf["score"],
        confidence_category=conf["category"],
        flag_for_review=conf["flag"],
        query_type=qtype,
        hallucination_verdict=verdict,
        sources=[SourceItem(section=c.get("section_name",""), chunk_type=c.get("chunk_type",""))
                 for c in top_chunks],
        suggested_questions=suggestions,
        latency_ms=int((time.time()-start)*1000),
    )
