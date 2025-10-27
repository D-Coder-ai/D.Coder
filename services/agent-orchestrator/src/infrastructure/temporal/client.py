"""
Temporal client initialization and management
"""


from temporalio.client import Client

from src.infrastructure.config.settings import settings


class TemporalClient:
    """Temporal client wrapper"""

    def __init__(self):
        self._client: Client | None = None

    async def connect(self) -> None:
        """Connect to Temporal server"""
        if self._client:
            return

        self._client = await Client.connect(
            settings.TEMPORAL_HOST,
            namespace=settings.TEMPORAL_NAMESPACE
        )

    async def disconnect(self) -> None:
        """Disconnect from Temporal server"""
        if self._client:
            await self._client.close()
            self._client = None

    @property
    def client(self) -> Client:
        """Get Temporal client"""
        if not self._client:
            raise RuntimeError("Temporal client not connected")
        return self._client

    @property
    def is_connected(self) -> bool:
        """Check if connected to Temporal"""
        return self._client is not None


_temporal_client: TemporalClient | None = None


async def get_temporal_client() -> TemporalClient:
    """Get or create Temporal client singleton"""
    global _temporal_client

    if _temporal_client is None:
        _temporal_client = TemporalClient()
        await _temporal_client.connect()

    return _temporal_client
