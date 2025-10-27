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
