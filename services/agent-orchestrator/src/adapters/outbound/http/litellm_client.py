"""
LiteLLM Proxy client (direct connection, not via Kong)
"""

from typing import Any

from src.infrastructure.config.settings import settings
from src.infrastructure.http.client import HTTPClient


class LiteLLMClient:
    """
    Client for LiteLLM Proxy (OpenAI-compatible)
    """

    def __init__(self):
        self.client = HTTPClient(base_url=settings.LITELLM_BASE)

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int | None = None,
        stream: bool = False
    ) -> dict[str, Any]:
        """
        Create a chat completion

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            Chat completion response
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        response = await self.client.post("/v1/chat/completions", json=payload)
        return response.json()

    async def embedding(
        self,
        text: str,
        model: str = "text-embedding-ada-002"
    ) -> list[float]:
        """
        Create an embedding

        Args:
            text: Text to embed
            model: Embedding model

        Returns:
            Embedding vector
        """
        payload = {
            "model": model,
            "input": text
        }

        response = await self.client.post("/v1/embeddings", json=payload)
        data = response.json()
        return data["data"][0]["embedding"]
