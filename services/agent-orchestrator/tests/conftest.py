"""
Pytest configuration and fixtures
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.main import app


@pytest.fixture
def test_client():
    """Synchronous test client for FastAPI"""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Asynchronous test client for FastAPI"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
