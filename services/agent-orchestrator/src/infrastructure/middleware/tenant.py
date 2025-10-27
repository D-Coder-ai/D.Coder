"""
Multi-tenancy Middleware
"""

from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling multi-tenancy headers
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and extract tenant information
        """
        tenant_id = request.headers.get("X-Tenant-Id")
        platform_id = request.headers.get("X-Platform-Id")
        user_id = request.headers.get("X-User-Id")

        request.state.tenant_id = tenant_id
        request.state.platform_id = platform_id
        request.state.user_id = user_id

        response = await call_next(request)

        if tenant_id:
            response.headers["X-Tenant-Id"] = tenant_id
        if platform_id:
            response.headers["X-Platform-Id"] = platform_id

        return response
