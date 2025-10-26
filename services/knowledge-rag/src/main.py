"""
Knowledge & RAG Service - Document processing and semantic search
"""

from fastapi import FastAPI

app = FastAPI(
    title="knowledge-rag",
    description="Knowledge & RAG Service - Document processing and semantic search",
    version="1.0.0"
)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "knowledge-rag"}
