"""
Knowledge & RAG service client (via Kong Gateway)
"""

from typing import Any

from src.infrastructure.config.settings import settings
from src.infrastructure.http.client import HTTPClient


class RAGClient:
    """
    Client for Knowledge & RAG service
    """

    def __init__(self):
        base_url = f"{settings.KONG_BASE_URL}/rag/v1"
        self.client = HTTPClient(base_url=base_url)

    async def search(
        self,
        query: str,
        limit: int = 5,
        filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Search the knowledge base

        Args:
            query: Search query
            limit: Maximum number of results
            filters: Optional filters

        Returns:
            List of search results
        """
        payload = {
            "query": query,
            "limit": limit
        }

        if filters:
            payload["filters"] = filters

        response = await self.client.post("/rag/search", json=payload)
        data = response.json()
        return data.get("results", [])
