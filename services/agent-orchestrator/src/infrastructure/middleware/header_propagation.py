"""
Header Propagation Middleware
"""

from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.infrastructure.context import (
    set_platform_id,
    set_request_id,
    set_tenant_id,
    set_trace_id,
    set_user_id,
)


class HeaderPropagationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for propagating headers to context variables
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Extract headers and set in context for outbound calls
        """
        if request_id := request.headers.get("X-Request-Id"):
            set_request_id(request_id)
        elif hasattr(request.state, "request_id"):
            set_request_id(request.state.request_id)

        if tenant_id := request.headers.get("X-Tenant-Id"):
            set_tenant_id(tenant_id)
        elif hasattr(request.state, "tenant_id"):
            set_tenant_id(request.state.tenant_id)

        if platform_id := request.headers.get("X-Platform-Id"):
            set_platform_id(platform_id)
        elif hasattr(request.state, "platform_id"):
            set_platform_id(request.state.platform_id)

        if user_id := request.headers.get("X-User-Id"):
            set_user_id(user_id)
        elif hasattr(request.state, "user_id"):
            set_user_id(request.state.user_id)

        if trace_id := request.headers.get("X-Trace-Id"):
            set_trace_id(trace_id)
        elif hasattr(request.state, "trace_id"):
            set_trace_id(request.state.trace_id)

        response = await call_next(request)

        return response
