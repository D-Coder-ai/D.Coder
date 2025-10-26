"""
Integrations Service - JIRA, Bitbucket, Confluence, SharePoint connectors
"""

from fastapi import FastAPI

app = FastAPI(
    title="integrations",
    description="Integrations Service - JIRA, Bitbucket, Confluence, SharePoint connectors",
    version="1.0.0"
)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "integrations"}
