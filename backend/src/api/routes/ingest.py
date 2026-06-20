"""
ingest.py — Author: Suresh D R | AI Product Developer & Technology Mentor
POST /ingest — Trigger document ingestion pipeline.
"""
import uuid
from fastapi import APIRouter, BackgroundTasks
from src.api.schemas import IngestRequest, IngestResponse
from src.ingestion.bulk_load import run as bulk_load_run

router = APIRouter()

def run_ingestion():
    try:
        bulk_load_run()
    except Exception as e:
        print(f"Ingestion error: {e}")

@router.post("/ingest", response_model=IngestResponse)
async def ingest_endpoint(req: IngestRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    background_tasks.add_task(run_ingestion)
    return IngestResponse(
        job_id=job_id,
        status="queued",
        message="Ingestion started in background. Documents will be ready in 2-5 minutes.",
    )
