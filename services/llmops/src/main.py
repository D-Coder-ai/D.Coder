"""
LLMOps Platform Service - Prompt engineering, experimentation, evaluation
"""

from fastapi import FastAPI

app = FastAPI(
    title="llmops",
    description="LLMOps Platform Service - Prompt engineering, experimentation, evaluation",
    version="1.0.0"
)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "llmops"}
