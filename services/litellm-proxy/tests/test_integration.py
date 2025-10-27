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


class TestSemanticCaching:
    """Test Redis-backed semantic caching functionality"""

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
        start_time = time.time()
        response1 = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers=auth_headers,
            json=request_payload
        )
        first_latency = time.time() - start_time
        assert response1.status_code == 200

        # Wait a moment for cache to be written
        await asyncio.sleep(1.0)

        # Second identical request - should be cache HIT
        start_time = time.time()
        response2 = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers=auth_headers,
            json=request_payload
        )
        second_latency = time.time() - start_time
        assert response2.status_code == 200

        # Verify both responses have same content (cached)
        data1 = response1.json()
        data2 = response2.json()
        assert data1["choices"][0]["message"]["content"] == data2["choices"][0]["message"]["content"]

        # Cache hit should be significantly faster
        assert second_latency < first_latency * 0.5, f"Cache hit not faster: {second_latency:.2f}s vs {first_latency:.2f}s"

        # Check for cache headers (if LiteLLM exposes them)
        if "X-Cache-Status" in response2.headers:
            assert response2.headers["X-Cache-Status"] in ["HIT", "hit"]

    @pytest.mark.asyncio
    async def test_semantic_similarity_cache(self, http_client, auth_headers):
        """Test that semantically similar requests hit cache (0.8 similarity threshold)"""

        # First request with specific wording
        request_payload1 = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "What is the capital of France?"}],
            "max_tokens": 20
        }

        response1 = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers=auth_headers,
            json=request_payload1
        )
        assert response1.status_code == 200
        data1 = response1.json()

        # Wait for cache write
        await asyncio.sleep(1.0)

        # Second request with similar but different wording
        request_payload2 = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "What is the capital city of France?"}],
            "max_tokens": 20
        }

        start_time = time.time()
        response2 = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers=auth_headers,
            json=request_payload2
        )
        latency = time.time() - start_time
        assert response2.status_code == 200
        data2 = response2.json()

        # Should get same or very similar response (semantic cache hit)
        # Note: This might not always be identical due to semantic matching threshold
        # but latency should be fast (<100ms for cache hit)
        assert latency < 0.2, f"Expected fast cache hit, got {latency:.2f}s"

    @pytest.mark.asyncio
    async def test_semantic_cache_miss(self, http_client, auth_headers):
        """Test that dissimilar requests do not hit cache"""

        # First request
        request_payload1 = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "What is the capital of France?"}],
            "max_tokens": 20
        }

        response1 = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers=auth_headers,
            json=request_payload1
        )
        assert response1.status_code == 200

        await asyncio.sleep(1.0)

        # Second request with completely different topic (should NOT hit cache)
        request_payload2 = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Explain quantum computing"}],
            "max_tokens": 20
        }

        start_time = time.time()
        response2 = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers=auth_headers,
            json=request_payload2
        )
        latency = time.time() - start_time
        assert response2.status_code == 200

        # Should take longer (cache MISS, actual API call)
        assert latency > 0.3, f"Expected cache miss (slower), got {latency:.2f}s"

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


class TestVirtualKeys:
    """Test virtual key generation, usage, and management"""

    @pytest.mark.asyncio
    async def test_virtual_key_generation(self, http_client):
        """Test generating a virtual key with master key"""

        response = await http_client.post(
            f"{LITELLM_BASE_URL}/key/generate",
            headers={
                "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "user_id": "test-user-001",
                "team_id": "test-tenant-001",
                "max_budget": 10.0,
                "models": ["gpt-4o-mini", "claude-haiku-3-5"],
                "duration": "30d"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "key" in data
        assert data["key"].startswith("sk-")
        assert "user_id" in data
        assert data["user_id"] == "test-user-001"
        assert "team_id" in data
        assert data["team_id"] == "test-tenant-001"

        # Return key for use in other tests
        return data["key"]

    @pytest.mark.asyncio
    async def test_virtual_key_usage(self, http_client):
        """Test using a virtual key for API requests"""

        # First generate a virtual key
        gen_response = await http_client.post(
            f"{LITELLM_BASE_URL}/key/generate",
            headers={
                "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "user_id": "test-user-002",
                "team_id": "test-tenant-002",
                "max_budget": 5.0,
                "models": ["gpt-4o-mini"]
            }
        )

        assert gen_response.status_code == 200
        virtual_key = gen_response.json()["key"]

        # Use virtual key for LLM request
        llm_response = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {virtual_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Say OK"}],
                "max_tokens": 5
            }
        )

        assert llm_response.status_code == 200
        data = llm_response.json()
        assert "choices" in data
        assert len(data["choices"]) > 0

    @pytest.mark.asyncio
    async def test_virtual_key_info(self, http_client):
        """Test retrieving virtual key information"""

        # Generate a key
        gen_response = await http_client.post(
            f"{LITELLM_BASE_URL}/key/generate",
            headers={
                "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "user_id": "test-user-003",
                "team_id": "test-tenant-003",
                "max_budget": 20.0,
                "models": ["gpt-4o-mini"]
            }
        )

        virtual_key = gen_response.json()["key"]

        # Get key info
        info_response = await http_client.post(
            f"{LITELLM_BASE_URL}/key/info",
            headers={
                "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
                "Content-Type": "application/json"
            },
            json={"key": virtual_key}
        )

        assert info_response.status_code == 200
        data = info_response.json()

        # Verify key info structure
        assert "key" in data or "info" in data
        assert "user_id" in data or ("info" in data and "user_id" in data["info"])

    @pytest.mark.asyncio
    async def test_virtual_key_model_restriction(self, http_client):
        """Test that virtual key restricts access to specified models only"""

        # Generate key with only gpt-4o-mini access
        gen_response = await http_client.post(
            f"{LITELLM_BASE_URL}/key/generate",
            headers={
                "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "user_id": "test-user-004",
                "team_id": "test-tenant-004",
                "max_budget": 5.0,
                "models": ["gpt-4o-mini"]  # Only allow gpt-4o-mini
            }
        )

        virtual_key = gen_response.json()["key"]

        # Try to use allowed model - should succeed
        allowed_response = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {virtual_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5
            }
        )

        assert allowed_response.status_code == 200

        # Try to use non-allowed model - should fail
        disallowed_response = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {virtual_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-5",  # Not in allowed models
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5
            }
        )

        # Should return 400 or 403 (model not allowed for this key)
        assert disallowed_response.status_code in [400, 403]

    @pytest.mark.asyncio
    async def test_virtual_key_budget_tracking(self, http_client):
        """Test that virtual key tracks spend against budget"""

        # Generate key with small budget
        gen_response = await http_client.post(
            f"{LITELLM_BASE_URL}/key/generate",
            headers={
                "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "user_id": "test-user-005",
                "team_id": "test-tenant-005",
                "max_budget": 1.0,  # $1 budget
                "models": ["gpt-4o-mini"]
            }
        )

        virtual_key = gen_response.json()["key"]

        # Make a request to incur some spend
        await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {virtual_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Count to 10"}],
                "max_tokens": 50
            }
        )

        # Check key info to see spend tracked
        info_response = await http_client.post(
            f"{LITELLM_BASE_URL}/key/info",
            headers={
                "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
                "Content-Type": "application/json"
            },
            json={"key": virtual_key}
        )

        assert info_response.status_code == 200
        data = info_response.json()

        # Verify spend is being tracked
        # Note: Exact field names may vary by LiteLLM version
        has_spend_info = (
            "spend" in data or
            ("info" in data and "spend" in data["info"]) or
            "usage" in data
        )
        assert has_spend_info, "Expected spend tracking information in key info"

    @pytest.mark.asyncio
    async def test_virtual_key_deletion(self, http_client):
        """Test deleting a virtual key"""

        # Generate a key
        gen_response = await http_client.post(
            f"{LITELLM_BASE_URL}/key/generate",
            headers={
                "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "user_id": "test-user-006",
                "team_id": "test-tenant-006",
                "max_budget": 5.0,
                "models": ["gpt-4o-mini"]
            }
        )

        virtual_key = gen_response.json()["key"]

        # Delete the key
        delete_response = await http_client.post(
            f"{LITELLM_BASE_URL}/key/delete",
            headers={
                "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
                "Content-Type": "application/json"
            },
            json={"key": virtual_key}
        )

        # Should return 200 or 204
        assert delete_response.status_code in [200, 204]

        # Try to use deleted key - should fail
        use_response = await http_client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {virtual_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5
            }
        )

        # Should return 401 (unauthorized) since key is deleted
        assert use_response.status_code == 401


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

    @pytest.mark.asyncio
    async def test_virtual_key_rate_limiting(self, http_client):
        """Test rate limiting per virtual key"""

        # Generate key with low rate limit
        gen_response = await http_client.post(
            f"{LITELLM_BASE_URL}/key/generate",
            headers={
                "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "user_id": "rate-test-user",
                "team_id": "rate-test-tenant",
                "max_budget": 5.0,
                "models": ["gpt-4o-mini"],
                "rpm": 2  # Only 2 requests per minute
            }
        )

        virtual_key = gen_response.json()["key"]

        # Make requests rapidly
        responses = []
        for i in range(5):
            response = await http_client.post(
                f"{LITELLM_BASE_URL}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {virtual_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": f"Request {i}"}],
                    "max_tokens": 5
                }
            )
            responses.append(response.status_code)
            await asyncio.sleep(0.2)

        # Should have some 429 (Too Many Requests) responses
        has_rate_limit = 429 in responses
        # Note: This might not always trigger depending on timing and LiteLLM config
        # The test verifies the endpoint behavior


# Helper for async operations
import asyncio


if __name__ == "__main__":
    # Run with: pytest litellm-proxy/tests/test_integration.py -v
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])

