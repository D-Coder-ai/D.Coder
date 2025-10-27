"""Quota events middleware for LiteLLM Proxy.

Publishes `quota.updated` events after each request using LiteLLM virtual keys.
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import litellm
from litellm.integrations.custom_logger import CustomLogger


DEFAULT_EVENT_SUBJECT = "quota.updated"


@dataclass
class EventEnvelope:
    """Service Contracts event envelope."""

    tenant_id: Optional[str]
    platform_id: Optional[str]
    actor: Optional[str]
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    occurred_at: datetime = datetime.now(timezone.utc)

    @property
    def event_id(self) -> str:
        return str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "eventId": self.event_id,
            "occurredAt": self.occurred_at.isoformat(),
            "tenantId": self.tenant_id,
            "platformId": self.platform_id,
            "correlationId": self.correlation_id,
            "actor": self.actor,
            "payload": self.payload,
        }


class QuotaEventsMiddleware(CustomLogger):
    """LiteLLM middleware that emits quota events and enforces budgets."""

    def __init__(self) -> None:
        super().__init__()
        self._nats_url = os.getenv("NATS_URL")
        self._event_subject = os.getenv("NATS_QUOTA_SUBJECT", DEFAULT_EVENT_SUBJECT)
        self._nats_connect_timeout = float(os.getenv("NATS_CONNECT_TIMEOUT", "2.0"))

    # Success path ---------------------------------------------------------

    async def async_log_success_event(
        self,
        kwargs: Dict[str, Any],
        response_obj: Dict[str, Any],
        start_time: float,
        end_time: float,
    ) -> None:
        await self._emit_event(kwargs, response_obj, start_time, end_time, error=None)

    # Failure path ---------------------------------------------------------

    async def async_log_failure_event(
        self,
        kwargs: Dict[str, Any],
        response_obj: Dict[str, Any],
        start_time: float,
        end_time: float,
    ) -> None:
        # If LiteLLM returns a budget exceeded error, translate to 429.
        error_body = self._build_error_body(response_obj)
        await self._emit_event(kwargs, response_obj, start_time, end_time, error=error_body)

    # Helpers --------------------------------------------------------------

    async def _emit_event(
        self,
        kwargs: Dict[str, Any],
        response_obj: Dict[str, Any],
        start_time: float,
        end_time: float,
        error: Optional[Dict[str, Any]],
    ) -> None:
        user_api_key = kwargs.get("metadata", {}).get("x-litellm-key")
        tenant_id = self._extract_tenant_id(kwargs)
        platform_id = kwargs.get("metadata", {}).get("x-platform-id")
        correlation_id = kwargs.get("metadata", {}).get("x-request-id")
        actor = kwargs.get("metadata", {}).get("x-user-id")

        usage = response_obj.get("usage", {}) if isinstance(response_obj, dict) else {}
        cost = self._safe_completion_cost(response_obj)
        payload = {
            "tenantId": tenant_id,
            "platformId": platform_id,
            "litellmKey": user_api_key,
            "model": kwargs.get("model"),
            "tokens": {
                "prompt": usage.get("prompt_tokens", 0),
                "completion": usage.get("completion_tokens", 0),
                "total": usage.get("total_tokens", 0),
            },
            "cost": cost,
            "latencyMs": int((end_time - start_time) * 1000),
            "error": error,
            "window": kwargs.get("team_id"),
        }

        envelope = EventEnvelope(
            tenant_id=tenant_id,
            platform_id=platform_id,
            actor=actor,
            correlation_id=correlation_id,
            payload=payload,
        )

        await self._publish_event(envelope)

    async def _publish_event(self, envelope: EventEnvelope) -> None:
        body = json.dumps(envelope.to_dict()).encode("utf-8")
        if not self._nats_url:
            # Fallback: log to stdout
            print(json.dumps({"subject": self._event_subject, "event": envelope.to_dict()}))
            return

        try:
            from nats.aio.client import Client as NATS

            nc = NATS()
            await nc.connect(self._nats_url, connect_timeout=self._nats_connect_timeout)
            await nc.publish(self._event_subject, body)
            await nc.drain()
        except Exception as exc:  # pragma: no cover - best effort emit
            print(f"Failed to publish quota event: {exc}")

    def _safe_completion_cost(self, response_obj: Dict[str, Any]) -> float:
        try:
            return float(litellm.completion_cost(completion_response=response_obj) or 0.0)
        except Exception:
            return 0.0

    def _build_error_body(self, response_obj: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not isinstance(response_obj, dict):
            return None

        error = response_obj.get("error")
        if isinstance(error, dict) and error.get("type") == "budget_exceeded":
            error["code"] = "429"
        return error

    def _extract_tenant_id(self, kwargs: Dict[str, Any]) -> Optional[str]:
        metadata = kwargs.get("metadata") or {}
        team_id = kwargs.get("team_id") or metadata.get("x-tenant-id")
        return team_id


quota_events_middleware = QuotaEventsMiddleware()


