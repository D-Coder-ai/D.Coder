"""
NATS event subscriber
"""

import asyncio
import json
from collections.abc import Callable

from src.domain.events.schemas import EventEnvelope
from src.infrastructure.nats.client import NATSClient


class EventSubscriber:
    """Subscriber for events from NATS JetStream"""

    def __init__(self, client: NATSClient):
        self.client = client
        self._subscriptions = []

    async def subscribe(
        self,
        stream_name: str,
        subject: str,
        consumer_name: str,
        handler: Callable[[EventEnvelope], None]
    ) -> None:
        """
        Subscribe to events from a JetStream stream

        Args:
            stream_name: Stream name (e.g., "WORKFLOWS")
            subject: Subject filter (e.g., "integration.*")
            consumer_name: Consumer name for durable subscription
            handler: Async callback function for handling events
        """
        if not self.client.is_connected:
            raise RuntimeError("NATS client not connected")

        psub = await self.client.jetstream.pull_subscribe(
            subject=subject,
            durable=consumer_name,
            stream=stream_name
        )

        self._subscriptions.append(psub)

        asyncio.create_task(self._process_messages(psub, handler))

    async def _process_messages(self, subscription, handler: Callable) -> None:
        """Process messages from subscription"""
        while True:
            try:
                messages = await subscription.fetch(batch=10, timeout=1)

                for msg in messages:
                    try:
                        event_data = json.loads(msg.data.decode('utf-8'))
                        event = EventEnvelope(**event_data)

                        await handler(event)

                        await msg.ack()
                    except Exception:
                        await msg.nak()

            except TimeoutError:
                continue
            except Exception:
                await asyncio.sleep(1)

    async def unsubscribe_all(self) -> None:
        """Unsubscribe from all subscriptions"""
        for sub in self._subscriptions:
            try:
                await sub.unsubscribe()
            except Exception:
                pass

        self._subscriptions.clear()
