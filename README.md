# Insurance Policy RAG Chatbot
**Author: Suresh D R | AI Product Developer & Technology Mentor**

AI-powered insurance policy Q&A system using Retrieval Augmented Generation.

## Quick Start
```bash
cp backend/.env.example backend/.env   # add your keys
docker compose up --build              # runs locally
```
Open http://localhost:3000

## Full Instructions
See [HOW_TO_RUN.md](HOW_TO_RUN.md)

## Stack
- **Backend:** FastAPI · ChromaDB · OpenAI GPT-4o · BM25 · sentence-transformers
- **Frontend:** React · Node.js · Axios
- **Infra:** Docker · AWS EKS · GitHub Actions · ECR
