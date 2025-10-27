"""
Event schemas following global conventions
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class EventEnvelope(BaseModel):
    """
    Standard event envelope following platform conventions
    """
    eventId: str = Field(default_factory=lambda: str(uuid4()))
    occurredAt: datetime = Field(default_factory=datetime.utcnow)
    tenantId: str | None = None
    platformId: str | None = None
    correlationId: str
    actor: str | None = None
    payload: dict[str, Any]


class WorkflowStartedPayload(BaseModel):
    """Payload for workflow.started event"""
    workflowId: str
    runId: str
    input: dict[str, Any]


class WorkflowStepCompletedPayload(BaseModel):
    """Payload for workflow.step.completed event"""
    workflowId: str
    stepId: str
    result: dict[str, Any]
    latencyMs: float


class WorkflowErrorPayload(BaseModel):
    """Payload for workflow.error event"""
    workflowId: str
    stepId: str | None = None
    code: str
    message: str


class WorkflowCompletedPayload(BaseModel):
    """Payload for workflow.completed event"""
    workflowId: str
    result: dict[str, Any]
    totalLatencyMs: float
