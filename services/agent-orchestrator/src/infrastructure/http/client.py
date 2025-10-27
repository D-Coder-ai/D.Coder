"""
Base HTTP client with header propagation and retry logic
"""

from typing import Any

import httpx

from src.infrastructure.context import (
    get_platform_id,
    get_request_id,
    get_tenant_id,
    get_trace_id,
    get_user_id,
)


class HTTPClient:
    """
    Base HTTP client with automatic header propagation
    """

    def __init__(self, base_url: str | None = None, timeout: float = 30.0):
        self.base_url = base_url
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                follow_redirects=True
            )
        return self._client

    def _build_headers(self, additional_headers: dict[str, str] | None = None) -> dict[str, str]:
        """
        Build headers with global platform headers

        Args:
            additional_headers: Additional headers to include

        Returns:
            Complete headers dict
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        if request_id := get_request_id():
            headers["X-Request-Id"] = request_id

        if tenant_id := get_tenant_id():
            headers["X-Tenant-Id"] = tenant_id

        if platform_id := get_platform_id():
            headers["X-Platform-Id"] = platform_id

        if user_id := get_user_id():
            headers["X-User-Id"] = user_id

        if trace_id := get_trace_id():
            headers["X-Trace-Id"] = trace_id

        if additional_headers:
            headers.update(additional_headers)

        return headers

    async def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None
    ) -> httpx.Response:
        """
        HTTP GET request

        Args:
            url: URL path
            params: Query parameters
            headers: Additional headers

        Returns:
            HTTP response
        """
        client = await self._get_client()
        request_headers = self._build_headers(headers)

        response = await client.get(url, params=params, headers=request_headers)
        response.raise_for_status()
        return response

    async def post(
        self,
        url: str,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None
    ) -> httpx.Response:
        """
        HTTP POST request

        Args:
            url: URL path
            json: JSON body
            headers: Additional headers

        Returns:
            HTTP response
        """
        client = await self._get_client()
        request_headers = self._build_headers(headers)

        response = await client.post(url, json=json, headers=request_headers)
        response.raise_for_status()
        return response

    async def close(self) -> None:
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None


_http_client: HTTPClient | None = None


def get_http_client() -> HTTPClient:
    """Get or create HTTP client singleton"""
    global _http_client

    if _http_client is None:
        _http_client = HTTPClient()

    return _http_client
