"""
Platform API client (via Kong Gateway)
"""

from typing import Any

from src.infrastructure.config.settings import settings
from src.infrastructure.http.client import HTTPClient


class PlatformAPIClient:
    """
    Client for Platform API via Kong Gateway
    """

    def __init__(self):
        self.client = HTTPClient(base_url=settings.PLATFORM_API_BASE)

    async def get_tenant_config(self, tenant_id: str) -> dict[str, Any]:
        """
        Get tenant configuration

        Args:
            tenant_id: Tenant ID

        Returns:
            Tenant configuration
        """
        response = await self.client.get(f"/tenants/{tenant_id}")
        return response.json()

    async def get_provider_config(self, tenant_id: str, provider: str) -> dict[str, Any]:
        """
        Get LLM provider configuration for tenant

        Args:
            tenant_id: Tenant ID
            provider: Provider name (openai, anthropic, etc.)

        Returns:
            Provider configuration
        """
        response = await self.client.get(f"/tenants/{tenant_id}/providers/{provider}")
        return response.json()

    async def check_quota(self, tenant_id: str) -> dict[str, Any]:
        """
        Check quota status for tenant

        Args:
            tenant_id: Tenant ID

        Returns:
            Quota information
        """
        response = await self.client.get(f"/tenants/{tenant_id}/quotas")
        return response.json()
