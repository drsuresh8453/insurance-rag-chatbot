"""
schemas.py — Author: Suresh D R | AI Product Developer & Technology Mentor
Pydantic request/response models for all API endpoints.
"""
from pydantic import BaseModel
from typing import Optional, List

class QueryRequest(BaseModel):
    question:    str
    tenant_id:   str = "star-health"
    user_id:     str = "anonymous"
    plan_filter: Optional[str] = None

class SourceItem(BaseModel):
    section:    str
    chunk_type: str

class QueryResponse(BaseModel):
    question:             str
    answer:               str
    confidence_score:     float
    confidence_category:  str
    flag_for_review:      bool
    query_type:           str
    hallucination_verdict:str
    sources:              List[SourceItem]
    suggested_questions:  List[str]
    latency_ms:           int

class IngestRequest(BaseModel):
    s3_key:    Optional[str] = None
    load_all:  bool = False
    tenant_id: str  = "star-health"

class IngestResponse(BaseModel):
    job_id:  str
    status:  str
    message: str

class HealthResponse(BaseModel):
    status:    str
    version:   str
    chroma_ok: bool
    s3_ok:     bool
