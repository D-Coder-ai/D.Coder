"""
Event service for publishing workflow events
"""

from typing import Any

from src.domain.events.schemas import (
    EventEnvelope,
    WorkflowCompletedPayload,
    WorkflowErrorPayload,
    WorkflowStartedPayload,
    WorkflowStepCompletedPayload,
)
from src.domain.events.types import (
    WORKFLOW_COMPLETED,
    WORKFLOW_ERROR,
    WORKFLOW_STARTED,
    WORKFLOW_STEP_COMPLETED,
)
from src.infrastructure.context import get_platform_id, get_request_id, get_tenant_id, get_user_id
from src.infrastructure.nats.client import NATSClient
from src.infrastructure.nats.publisher import EventPublisher


class EventService:
    """Service for publishing workflow events"""

    def __init__(self, client: NATSClient):
        self.publisher = EventPublisher(client)

    def _create_envelope(self, payload: dict[str, Any]) -> EventEnvelope:
        """Create event envelope with context from request"""
        return EventEnvelope(
            tenantId=get_tenant_id(),
            platformId=get_platform_id(),
            correlationId=get_request_id() or "",
            actor=get_user_id(),
            payload=payload
        )

    async def publish_workflow_started(
        self,
        workflow_id: str,
        run_id: str,
        input_data: dict[str, Any]
    ) -> None:
        """Publish workflow.started event"""
        payload = WorkflowStartedPayload(
            workflowId=workflow_id,
            runId=run_id,
            input=input_data
        )

        envelope = self._create_envelope(payload.model_dump())
        await self.publisher.publish_event(WORKFLOW_STARTED, envelope)

    async def publish_workflow_step_completed(
        self,
        workflow_id: str,
        step_id: str,
        result: dict[str, Any],
        latency_ms: float
    ) -> None:
        """Publish workflow.step.completed event"""
        payload = WorkflowStepCompletedPayload(
            workflowId=workflow_id,
            stepId=step_id,
            result=result,
            latencyMs=latency_ms
        )

        envelope = self._create_envelope(payload.model_dump())
        await self.publisher.publish_event(WORKFLOW_STEP_COMPLETED, envelope)

    async def publish_workflow_error(
        self,
        workflow_id: str,
        code: str,
        message: str,
        step_id: str | None = None
    ) -> None:
        """Publish workflow.error event"""
        payload = WorkflowErrorPayload(
            workflowId=workflow_id,
            stepId=step_id,
            code=code,
            message=message
        )

        envelope = self._create_envelope(payload.model_dump())
        await self.publisher.publish_event(WORKFLOW_ERROR, envelope)

    async def publish_workflow_completed(
        self,
        workflow_id: str,
        result: dict[str, Any],
        total_latency_ms: float
    ) -> None:
        """Publish workflow.completed event"""
        payload = WorkflowCompletedPayload(
            workflowId=workflow_id,
            result=result,
            totalLatencyMs=total_latency_ms
        )

        envelope = self._create_envelope(payload.model_dump())
        await self.publisher.publish_event(WORKFLOW_COMPLETED, envelope)
