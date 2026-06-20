"""
test_retrieval.py — Author: Suresh D R | AI Product Developer & Technology Mentor
Unit tests for RRF merge and confidence scorer.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_rrf_merge_combines_results():
    from src.retrieval.hybrid_search import rrf_merge
    l1 = [{"chunk_id":"a","text":"a"},{"chunk_id":"b","text":"b"}]
    l2 = [{"chunk_id":"b","text":"b"},{"chunk_id":"c","text":"c"}]
    result = rrf_merge(l1, l2)
    ids = [r["chunk_id"] for r in result]
    assert "b" in ids
    assert result[0]["chunk_id"] == "b"  # b appears in both lists

def test_rrf_merge_no_duplicates():
    from src.retrieval.hybrid_search import rrf_merge
    l1 = [{"chunk_id":"a","text":"a"},{"chunk_id":"b","text":"b"}]
    l2 = [{"chunk_id":"a","text":"a"},{"chunk_id":"c","text":"c"}]
    result = rrf_merge(l1, l2)
    ids = [r["chunk_id"] for r in result]
    assert len(ids) == len(set(ids))

def test_confidence_medium_range():
    from src.pipeline.confidence import compute_confidence
    conf = compute_confidence([0.65,0.60,0.55], [5.0,4.0,3.0], True, "comparison")
    assert conf["category"] in ["MEDIUM","HIGH"]

def test_confidence_breakdown_keys():
    from src.pipeline.confidence import compute_confidence
    conf = compute_confidence([0.7], [6.0], True, "factual")
    assert "similarity" in conf["breakdown"]
    assert "rerank_norm" in conf["breakdown"]
    assert "hall_penalty" in conf["breakdown"]
