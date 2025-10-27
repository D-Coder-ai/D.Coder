"""
Unit tests for HTTP clients
"""


import pytest

from src.infrastructure.context import set_request_id, set_tenant_id
from src.infrastructure.http.client import HTTPClient


@pytest.mark.asyncio
async def test_http_client_builds_headers():
    """Test that HTTP client builds headers correctly"""
    set_request_id("test-request-id")
    set_tenant_id("test-tenant")

    client = HTTPClient(base_url="http://test.com")
    headers = client._build_headers()

    assert headers["X-Request-Id"] == "test-request-id"
    assert headers["X-Tenant-Id"] == "test-tenant"
    assert headers["Content-Type"] == "application/json"

    await client.close()


@pytest.mark.asyncio
async def test_http_client_custom_headers():
    """Test that custom headers are merged"""
    client = HTTPClient()

    headers = client._build_headers({"X-Custom": "value"})

    assert headers["X-Custom"] == "value"
    assert headers["Content-Type"] == "application/json"

    await client.close()
