"""
Logging Middleware
"""

import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request/response logging and request ID management
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and log details
        """
        request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        trace_id = request.headers.get("X-Trace-Id", request_id)

        request.state.request_id = request_id
        request.state.trace_id = trace_id

        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time

        response.headers["X-Request-Id"] = request_id
        response.headers["X-Trace-Id"] = trace_id
        response.headers["X-Process-Time"] = str(process_time)

        return response
