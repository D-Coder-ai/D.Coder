"""
JWT Authentication Middleware
"""

import logging
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.infrastructure.auth.jwt import validate_token

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for JWT token validation (R1: warn-only mode)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and validate JWT if present
        """
        auth_header = request.headers.get("Authorization", "")

        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

            is_valid, claims, error = validate_token(token)

            if not is_valid:
                logger.warning(f"Invalid JWT token: {error}")

            if claims:
                request.state.user_claims = claims
                request.state.user_id = claims.get("sub") or claims.get("user_id")

        response = await call_next(request)

        return response
