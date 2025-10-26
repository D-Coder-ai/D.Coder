"""
Multi-tenancy Middleware
"""

from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling multi-tenancy
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and extract tenant information
        """
        # Extract tenant from headers or subdomain
        tenant_id = request.headers.get("X-Tenant-Id")

        # If not in header, try to extract from subdomain
        if not tenant_id:
            host = request.headers.get("host", "")
            # Example: tenant1.platform.com -> tenant1
            if "." in host:
                tenant_id = host.split(".")[0]

        # Store tenant ID in request state for use in endpoints
        request.state.tenant_id = tenant_id

        # TODO: Validate tenant exists and is active
        # if tenant_id:
        #     tenant = await get_tenant(tenant_id)
        #     if not tenant or tenant.status != "active":
        #         return Response(
        #             content="Invalid or inactive tenant",
        #             status_code=403
        #         )

        # Process request
        response = await call_next(request)

        # Add tenant ID to response headers
        if tenant_id:
            response.headers["X-Tenant-Id"] = tenant_id

        return response