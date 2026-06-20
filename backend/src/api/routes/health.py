"""
health.py — Author: Suresh D R | AI Product Developer & Technology Mentor
GET /health — liveness and readiness probe for Kubernetes.
"""
import os
from fastapi import APIRouter
from src.api.schemas import HealthResponse
from src.ingestion.embedder import get_collection
from src.ingestion.s3_loader import list_raw_files

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health():
    chroma_ok = False
    s3_ok     = False
    try:
        col = get_collection()
        chroma_ok = col.count() >= 0
    except: pass
    try:
        list_raw_files()
        s3_ok = True
    except: pass
    return HealthResponse(
        status="ok" if chroma_ok and s3_ok else "degraded",
        version="2.0.0",
        chroma_ok=chroma_ok,
        s3_ok=s3_ok,
    )
