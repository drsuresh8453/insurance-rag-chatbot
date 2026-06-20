"""
main.py — Author: Suresh D R | AI Product Developer & Technology Mentor
FastAPI application entry point. Registers routes, sets up CORS.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import health, query, ingest

app = FastAPI(
    title="Insurance Policy RAG Chatbot",
    description="AI-powered insurance policy Q&A — Author: Suresh D R",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(query.router,  prefix="/api", tags=["Query"])
app.include_router(ingest.router, prefix="/api", tags=["Ingest"])

@app.get("/")
async def root():
    return {
        "name":    "Insurance Policy RAG Chatbot",
        "author":  "Suresh D R | AI Product Developer & Technology Mentor",
        "version": "1.0.0",
        "docs":    "/docs",
    }
