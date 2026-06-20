"""
test_pipeline.py — Author: Suresh D R | AI Product Developer & Technology Mentor
Integration tests for the query pipeline using mocks.
"""
import pytest
from unittest.mock import patch, MagicMock
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

@patch("src.pipeline.classifier.OpenAI")
def test_classifier_returns_valid_type(mock_openai):
    mock_resp = MagicMock()
    mock_resp.choices[0].message.content = "factual"
    mock_openai.return_value.chat.completions.create.return_value = mock_resp
    from src.pipeline.classifier import classify
    result = classify("What is the room rent limit?")
    assert result in ["factual","comparison","summarisation","multi_hop",
                      "eligibility","claims_process","calculation","negation"]

@patch("src.pipeline.classifier.OpenAI")
def test_classifier_fallback_to_factual(mock_openai):
    mock_resp = MagicMock()
    mock_resp.choices[0].message.content = "unknown_type"
    mock_openai.return_value.chat.completions.create.return_value = mock_resp
    from src.pipeline.classifier import classify
    result = classify("some question")
    assert result == "factual"

def test_confidence_high():
    from src.pipeline.confidence import compute_confidence
    conf = compute_confidence([0.92,0.88,0.85], [8.0,6.0,5.0], True, "factual")
    assert conf["category"] == "HIGH"
    assert conf["score"] >= 0.75

def test_confidence_low_when_hallucination():
    from src.pipeline.confidence import compute_confidence
    conf = compute_confidence([0.55,0.50,0.48], [3.0,2.0,1.0], False, "factual")
    assert conf["category"] == "LOW"
    assert conf["flag"] is True

def test_output_guard_adds_disclaimer():
    from src.guardrails.output_guard import check_output
    answer = "Room rent is covered up to Rs.3,000 per day as per Section 3.4."
    processed, issues = check_output(answer, "factual", True)
    assert "*" in processed
