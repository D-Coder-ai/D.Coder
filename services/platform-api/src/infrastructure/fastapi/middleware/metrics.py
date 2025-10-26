"""
Metrics Middleware for Prometheus
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware for collecting Prometheus metrics
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and collect metrics
        """
        # Start timer
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate request duration
        duration = time.time() - start_time

        # TODO: Implement actual metrics collection
        # metrics.http_request_duration_seconds.labels(
        #     method=request.method,
        #     endpoint=request.url.path,
        #     status=response.status_code
        # ).observe(duration)

        # metrics.http_requests_total.labels(
        #     method=request.method,
        #     endpoint=request.url.path,
        #     status=response.status_code
        # ).inc()

        return response