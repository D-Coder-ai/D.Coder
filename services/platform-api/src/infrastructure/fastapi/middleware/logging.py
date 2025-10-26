"""
Logging Middleware
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request/response logging
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and log details
        """
        # Generate request ID if not present
        request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))

        # Start timer
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate process time
        process_time = time.time() - start_time

        # Add headers
        response.headers["X-Request-Id"] = request_id
        response.headers["X-Process-Time"] = str(process_time)

        # TODO: Implement actual logging
        # logger.info(
        #     f"Request: {request.method} {request.url.path} "
        #     f"Status: {response.status_code} "
        #     f"Duration: {process_time:.3f}s"
        # )

        return response