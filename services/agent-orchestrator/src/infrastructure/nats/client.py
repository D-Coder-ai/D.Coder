"""
NATS client initialization and management
"""

import nats
from nats.js import JetStreamContext

from src.infrastructure.config.settings import settings


class NATSClient:
    """NATS client with JetStream support"""

    def __init__(self):
        self._nc: nats.NATS | None = None
        self._js: JetStreamContext | None = None

    async def connect(self) -> None:
        """Connect to NATS server"""
        if self._nc and self._nc.is_connected:
            return

        self._nc = await nats.connect(
            servers=[settings.NATS_URL],
            max_reconnect_attempts=-1,
            reconnect_time_wait=2
        )

        self._js = self._nc.jetstream()

    async def disconnect(self) -> None:
        """Disconnect from NATS server"""
        if self._nc and self._nc.is_connected:
            await self._nc.drain()
            await self._nc.close()

        self._nc = None
        self._js = None

    @property
    def jetstream(self) -> JetStreamContext:
        """Get JetStream context"""
        if not self._js:
            raise RuntimeError("NATS client not connected")
        return self._js

    @property
    def is_connected(self) -> bool:
        """Check if connected to NATS"""
        return self._nc is not None and self._nc.is_connected


_nats_client: NATSClient | None = None


async def get_nats_client() -> NATSClient:
    """Get or create NATS client singleton"""
    global _nats_client

    if _nats_client is None:
        _nats_client = NATSClient()
        await _nats_client.connect()

    return _nats_client
