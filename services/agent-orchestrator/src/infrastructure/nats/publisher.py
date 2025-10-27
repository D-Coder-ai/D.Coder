"""
NATS event publisher
"""

from src.domain.events.schemas import EventEnvelope
from src.infrastructure.nats.client import NATSClient


class EventPublisher:
    """Publisher for events to NATS JetStream"""

    def __init__(self, client: NATSClient):
        self.client = client

    async def publish_event(self, subject: str, event: EventEnvelope) -> None:
        """
        Publish an event to NATS JetStream

        Args:
            subject: NATS subject (e.g., "workflow.started")
            event: Event envelope with payload
        """
        if not self.client.is_connected:
            raise RuntimeError("NATS client not connected")

        event_data = event.model_dump_json()

        try:
            await self.client.jetstream.publish(
                subject=subject,
                payload=event_data.encode('utf-8')
            )
        except Exception as e:
            raise RuntimeError(f"Failed to publish event to {subject}: {str(e)}") from e
