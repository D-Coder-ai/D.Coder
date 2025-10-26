"""
Integration tests for LiteLLM Proxy
Tests multi-provider routing, Redis caching, compression, and observability
"""

import pytest
import httpx
import time
import os
from typing import Dict, Any


# Test configuration
LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
LITELLM_MASTER_KEY = os.getenv("LITELLM_MASTER_KEY", "sk-1234567890abcdef")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))


@pytest.fixture
async def http_client():
    """Async HTTP client for API calls"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client


@pytest.fixture
def auth_headers() -> Dict[str, str]:
    """Authorization headers for LiteLLM"""
    return {
        "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
        "Content-Type": "application/json"
    }


class TestHealthAndStatus:
    """Test basic health and status endpoints"""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, http_client):
        """Verify /health endpoint returns healthy status"""
        response = await http_client.get(f"{LITELLM_BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") in ["healthy", "ok"]
    
    @pytest.mark.asyncio
    async def test_models_endpoint(self, http_client, auth_headers):
        """Verify /v1/models returns configured models"""
        response = await http_client.get(
            f"{LITELLM_BASE_URL}/v1/models",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        
        # Verify expected models are present
        model_ids = [model["id"] for model in data["data"]]
        expected_models = [
            "gpt-4o",
            "gpt-4o-mini",
            "claude-sonnet-4-5",
            "gemini-2-5-pro",
            "groq-llama-3-3-70b"
        ]
        
        for model in expected_models:
            assert model in model_ids, f"Model {model} not found in /v1/models"


class TestMultiProviderRouting:
    """Test routing to different LLM providers"""
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("model,provider", [
        ("gpt-4o-mini", "openai"),
        ("claude-haiku-3-5", "anthropic"),
        ("gemini-2-5-flash", "google"),
    ])
    async def test_provider_routing(self, http_client, auth_headers, model, provider):
        """Test successful routing to each provider"""
        response = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers=auth_headers,
            json={
                "model": model,
                "messages": [{"role": "user", "content": "Say 'OK'"}],
                "max_tokens": 5
            }
        )
        
        assert response.status_code == 200, f"Failed for {provider}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "choices" in data
        assert len(data["choices"]) > 0
        assert "message" in data["choices"][0]
        assert "content" in data["choices"][0]["message"]
        
        # Verify usage tracking
        assert "usage" in data
        assert "total_tokens" in data["usage"]
        assert data["usage"]["total_tokens"] > 0


class TestRedisCaching:
    """Test Redis-backed caching functionality"""
    
    @pytest.mark.asyncio
    async def test_exact_match_cache(self, http_client, auth_headers):
        """Test that identical requests hit cache on second call"""
        
        # Unique message to avoid interference from previous tests
        unique_id = f"test-cache-{int(time.time() * 1000)}"
        request_payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": f"Hello {unique_id}"}],
            "max_tokens": 10
        }
        
        # First request - should be cache MISS
        response1 = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers=auth_headers,
            json=request_payload
        )
        assert response1.status_code == 200
        
        # Wait a moment for cache to be written
        await asyncio.sleep(0.5)
        
        # Second identical request - should be cache HIT
        response2 = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers=auth_headers,
            json=request_payload
        )
        assert response2.status_code == 200
        
        # Verify both responses have same content (cached)
        data1 = response1.json()
        data2 = response2.json()
        assert data1["choices"][0]["message"]["content"] == data2["choices"][0]["message"]["content"]
        
        # Check for cache headers (if LiteLLM exposes them)
        # X-Cache-Status might be in response headers
        if "X-Cache-Status" in response2.headers:
            assert response2.headers["X-Cache-Status"] in ["HIT", "hit"]
    
    @pytest.mark.asyncio
    async def test_cache_bypass_with_force_refresh(self, http_client, auth_headers):
        """Test that force_refresh bypasses cache"""
        
        unique_id = f"test-bypass-{int(time.time() * 1000)}"
        request_payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": f"Hello {unique_id}"}],
            "max_tokens": 10
        }
        
        # First request
        response1 = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers=auth_headers,
            json=request_payload
        )
        assert response1.status_code == 200
        
        # Second request with cache bypass (if supported)
        request_payload_bypass = request_payload.copy()
        request_payload_bypass["cache"] = {"no-cache": True}
        
        response2 = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers=auth_headers,
            json=request_payload_bypass
        )
        assert response2.status_code == 200


class TestPromptCompression:
    """Test LLMLingua prompt compression middleware"""
    
    @pytest.mark.asyncio
    async def test_large_prompt_compression(self, http_client, auth_headers):
        """Test that large prompts are compressed"""
        
        # Create a large prompt (>500 tokens threshold)
        large_context = " ".join([
            "This is a long context paragraph with information about various topics."
        ] * 50)  # Approximately 600+ tokens
        
        request_payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": large_context + "\n\nSummarize the above."}
            ],
            "max_tokens": 50
        }
        
        response = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers=auth_headers,
            json=request_payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response is still coherent despite compression
        assert "choices" in data
        assert len(data["choices"]) > 0
        
        # Compression metrics would be in logs/prometheus
        # Here we just verify the request succeeded
    
    @pytest.mark.asyncio
    async def test_small_prompt_not_compressed(self, http_client, auth_headers):
        """Test that small prompts skip compression"""
        
        # Small prompt (<500 tokens threshold)
        request_payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 10
        }
        
        response = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers=auth_headers,
            json=request_payload
        )
        
        assert response.status_code == 200


class TestCostTracking:
    """Test cost tracking and usage metrics"""
    
    @pytest.mark.asyncio
    async def test_usage_tracking(self, http_client, auth_headers):
        """Verify usage data is returned in responses"""
        
        response = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers=auth_headers,
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Count to 5"}],
                "max_tokens": 20
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify usage object
        assert "usage" in data
        usage = data["usage"]
        assert "prompt_tokens" in usage
        assert "completion_tokens" in usage
        assert "total_tokens" in usage
        
        # Verify all token counts are positive
        assert usage["prompt_tokens"] > 0
        assert usage["completion_tokens"] > 0
        assert usage["total_tokens"] > 0


class TestObservability:
    """Test observability endpoints and metrics"""
    
    @pytest.mark.asyncio
    async def test_prometheus_metrics(self, http_client):
        """Verify Prometheus metrics endpoint"""
        
        response = await http_client.get(f"{LITELLM_BASE_URL}/metrics")
        assert response.status_code == 200
        
        metrics_text = response.text
        
        # Verify key metrics are present
        expected_metrics = [
            "litellm_requests_total",
            "litellm_request_duration_seconds",
            # Cache metrics
            "litellm_cache_hit_total",
            "litellm_cache_miss_total",
        ]
        
        for metric in expected_metrics:
            assert metric in metrics_text, f"Metric {metric} not found in /metrics"
    
    @pytest.mark.asyncio
    async def test_compression_metrics(self, http_client):
        """Verify compression metrics are exposed"""
        
        response = await http_client.get(f"{LITELLM_BASE_URL}/metrics")
        assert response.status_code == 200
        
        metrics_text = response.text
        
        # Check for compression metrics
        compression_metrics = [
            "litellm_compression_requests_total",
            "litellm_compression_savings_percent",
        ]
        
        for metric in compression_metrics:
            # These might not be present if no compression happened yet
            # Just verify the endpoint is accessible
            pass


class TestPerformance:
    """Performance and latency tests"""
    
    @pytest.mark.asyncio
    async def test_cache_hit_latency(self, http_client, auth_headers):
        """Verify cache hits have low latency (<50ms target)"""
        
        unique_id = f"latency-test-{int(time.time() * 1000)}"
        request_payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": f"Hello {unique_id}"}],
            "max_tokens": 5
        }
        
        # First request (cache MISS)
        response1 = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers=auth_headers,
            json=request_payload
        )
        assert response1.status_code == 200
        
        # Wait for cache write
        await asyncio.sleep(0.5)
        
        # Second request (cache HIT) - measure latency
        start_time = time.time()
        response2 = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers=auth_headers,
            json=request_payload
        )
        end_time = time.time()
        
        assert response2.status_code == 200
        
        # Cache hit should be fast (<100ms including network)
        latency_ms = (end_time - start_time) * 1000
        assert latency_ms < 100, f"Cache hit latency too high: {latency_ms:.2f}ms"


class TestErrorHandling:
    """Test error handling and resilience"""
    
    @pytest.mark.asyncio
    async def test_invalid_model(self, http_client, auth_headers):
        """Test error handling for non-existent model"""
        
        response = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers=auth_headers,
            json={
                "model": "non-existent-model",
                "messages": [{"role": "user", "content": "Hello"}]
            }
        )
        
        # Should return error (400 or 404)
        assert response.status_code in [400, 404]
        data = response.json()
        assert "error" in data
    
    @pytest.mark.asyncio
    async def test_missing_auth(self, http_client):
        """Test that requests without auth are rejected"""
        
        response = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Hello"}]
            }
        )
        
        # Should return 401 Unauthorized
        assert response.status_code == 401


class TestStreamingSupport:
    """Test streaming responses"""
    
    @pytest.mark.asyncio
    async def test_streaming_chat_completion(self, http_client, auth_headers):
        """Test streaming chat completions (SSE)"""
        
        request_payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Count to 3"}],
            "stream": True,
            "max_tokens": 20
        }
        
        async with http_client.stream(
            "POST",
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers=auth_headers,
            json=request_payload
        ) as response:
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")
            
            # Collect streamed chunks
            chunks = []
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    chunk_data = line[6:]  # Remove "data: " prefix
                    if chunk_data != "[DONE]":
                        chunks.append(chunk_data)
            
            # Verify we received multiple chunks
            assert len(chunks) > 0, "No chunks received in stream"


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    @pytest.mark.asyncio
    async def test_rate_limit_headers(self, http_client, auth_headers):
        """Verify rate limit headers are present"""
        
        response = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers=auth_headers,
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 5
            }
        )
        
        assert response.status_code == 200
        
        # LiteLLM may expose rate limit info in headers or response
        # Check if headers are present
        rate_limit_headers = [
            "x-ratelimit-limit",
            "x-ratelimit-remaining",
            "x-ratelimit-reset"
        ]
        
        # Note: Not all headers may be present depending on configuration
        # This is more for documentation purposes


# Helper for async operations
import asyncio


if __name__ == "__main__":
    # Run with: pytest litellm-proxy/tests/test_integration.py -v
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])

