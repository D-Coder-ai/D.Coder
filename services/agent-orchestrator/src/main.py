"""
Agent Orchestration Service - Durable workflows with Temporal and LangGraph
"""

from fastapi import FastAPI

app = FastAPI(
    title="agent-orchestrator",
    description="Agent Orchestration Service - Durable workflows with Temporal and LangGraph",
    version="1.0.0"
)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "agent-orchestrator"}
