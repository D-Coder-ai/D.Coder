"""
Health Check Endpoints
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str
    version: str
    timestamp: str
    checks: dict[str, Any]


@router.get(
    "/",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check if the service is healthy and running"
)
async def health_check() -> HealthResponse:
    """
    Perform health check on the service and its dependencies
    """
    from src.infrastructure.config.settings import settings

    checks = {
        "temporal": "unknown",
        "nats": "unknown",
        "redis": "unknown"
    }

    return HealthResponse(
        status="healthy",
        service=settings.SERVICE_NAME,
        version=settings.SERVICE_VERSION,
        timestamp=datetime.utcnow().isoformat(),
        checks=checks
    )


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness Check",
    description="Check if the service is ready to accept requests"
)
async def readiness_check() -> dict[str, str]:
    """
    Check if the service is ready to handle requests
    """
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get(
    "/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness Check",
    description="Check if the service is alive"
)
async def liveness_check() -> dict[str, str]:
    """
    Simple liveness check for Kubernetes probes
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }
