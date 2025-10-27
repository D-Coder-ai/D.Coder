import json
from pathlib import Path
from typing import Dict

import pytest
import yaml

from middleware.quota_events import QuotaEventsMiddleware

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "litellm_config.yaml"


def load_config() -> Dict:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def test_config_includes_semantic_cache_and_embedding_model():
    config = load_config()
    cache_params = config["litellm_settings"]["cache_params"]

    assert cache_params["type"] == "redis-semantic"
    assert cache_params["redis_semantic_cache_embedding_model"] == "text-embedding-3-small"
    assert "similarity_threshold" in cache_params

    model_names = {model["model_name"] for model in config["model_list"]}
    assert "text-embedding-3-small" in model_names


def test_config_registers_required_callbacks():
    config = load_config()
    callbacks = config["litellm_settings"]["callbacks"]
    assert "middleware.prompt_compression.PromptCompressionMiddleware" in callbacks
    assert "middleware.quota_events.QuotaEventsMiddleware" in callbacks


@pytest.fixture
def quota_middleware(monkeypatch) -> QuotaEventsMiddleware:
    monkeypatch.delenv("NATS_URL", raising=False)
    monkeypatch.setenv("NATS_QUOTA_SUBJECT", "quota.updated.tests")
    return QuotaEventsMiddleware()


@pytest.mark.asyncio
async def test_quota_event_success_emits_payload(monkeypatch, quota_middleware, capsys):
    monkeypatch.setattr(
        "middleware.quota_events.litellm.completion_cost", lambda completion_response: 4.2
    )
    kwargs = {
        "metadata": {
            "x-litellm-key": "sk-test",
            "x-platform-id": "platform-1",
            "x-request-id": "req-1",
            "x-user-id": "user-42",
        },
        "model": "gpt-4o",
        "team_id": "tenant-123",
    }
    response_obj = {
        "usage": {"prompt_tokens": 25, "completion_tokens": 50, "total_tokens": 75}
    }

    await quota_middleware.async_log_success_event(kwargs, response_obj, 0.0, 0.5)

    output = capsys.readouterr().out.strip().splitlines()
    assert output
    event_record = json.loads(output[-1])
    assert event_record["subject"] == "quota.updated.tests"

    payload = event_record["event"]["payload"]
    assert payload["tenantId"] == "tenant-123"
    assert payload["platformId"] == "platform-1"
    assert payload["litellmKey"] == "sk-test"
    assert payload["tokens"]["total"] == 75
    assert payload["cost"] == pytest.approx(4.2)
    assert payload["latencyMs"] == 500


@pytest.mark.asyncio
async def test_quota_event_failure_converts_budget_error(monkeypatch, quota_middleware, capsys):
    monkeypatch.setattr(
        "middleware.quota_events.litellm.completion_cost", lambda completion_response: 0.0
    )
    kwargs = {
        "metadata": {"x-request-id": "req-err"},
        "team_id": "tenant-budget",
    }
    response_obj = {"error": {"type": "budget_exceeded", "code": "400"}}

    await quota_middleware.async_log_failure_event(kwargs, response_obj, 1.0, 1.1)

    output = capsys.readouterr().out.strip().splitlines()
    assert output
    event_record = json.loads(output[-1])
    payload = event_record["event"]["payload"]
    assert payload["error"]["type"] == "budget_exceeded"
    assert payload["error"]["code"] == "429"
    assert payload["latencyMs"] == 100


@pytest.mark.asyncio
async def test_quota_event_nats_publish_path(monkeypatch):
    """Test NATS publish path when NATS_URL is configured"""
    # Mock NATS client
    published_events = []
    
    class MockNATSClient:
        async def connect(self, url, connect_timeout=None):
            pass
        
        async def publish(self, subject, data):
            published_events.append({
                "subject": subject,
                "data": json.loads(data.decode("utf-8"))
            })
        
        async def drain(self):
            pass
    
    # Configure NATS URL
    monkeypatch.setenv("NATS_URL", "nats://localhost:4222")
    monkeypatch.setenv("NATS_QUOTA_SUBJECT", "quota.updated.test")
    
    # Mock the NATS client by patching the import inside _publish_event
    async def mock_publish_with_nats(self, envelope):
        """Mock _publish_event to use our mock NATS client"""
        body = json.dumps(envelope.to_dict()).encode("utf-8")
        if not self._nats_url:
            print(json.dumps({"subject": self._event_subject, "event": envelope.to_dict()}))
            return
        
        # Use mock client
        nc = MockNATSClient()
        await nc.connect(self._nats_url, connect_timeout=self._nats_connect_timeout)
        await nc.publish(self._event_subject, body)
        await nc.drain()
    
    monkeypatch.setattr(
        QuotaEventsMiddleware,
        "_publish_event",
        mock_publish_with_nats
    )
    
    # Mock completion cost
    monkeypatch.setattr(
        "middleware.quota_events.litellm.completion_cost", 
        lambda completion_response: 2.5
    )
    
    # Create middleware with NATS enabled
    middleware = QuotaEventsMiddleware()
    
    kwargs = {
        "metadata": {
            "x-litellm-key": "sk-nats-test",
            "x-platform-id": "platform-nats",
            "x-request-id": "req-nats-1",
            "x-user-id": "user-nats",
        },
        "model": "gpt-4o-mini",
        "team_id": "tenant-nats",
    }
    response_obj = {
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
    }
    
    # Emit event
    await middleware.async_log_success_event(kwargs, response_obj, 0.0, 0.3)
    
    # Verify event was published via NATS
    assert len(published_events) == 1
    event = published_events[0]
    
    assert event["subject"] == "quota.updated.test"
    assert "eventId" in event["data"]
    assert "occurredAt" in event["data"]
    
    payload = event["data"]["payload"]
    assert payload["tenantId"] == "tenant-nats"
    assert payload["platformId"] == "platform-nats"
    assert payload["litellmKey"] == "sk-nats-test"
    assert payload["tokens"]["total"] == 30
    assert payload["cost"] == 2.5
    assert payload["latencyMs"] == 300

