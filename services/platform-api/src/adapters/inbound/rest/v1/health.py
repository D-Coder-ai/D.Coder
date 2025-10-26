"""
Health Check Endpoints
"""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, status
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str
    version: str
    timestamp: str
    checks: Dict[str, Any]


router = APIRouter()


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
        "database": "healthy",  # TODO: Implement actual DB check
        "redis": "healthy",     # TODO: Implement actual Redis check
        "nats": "healthy"       # TODO: Implement actual NATS check
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
async def readiness_check() -> Dict[str, str]:
    """
    Check if the service is ready to handle requests
    """
    # TODO: Implement actual readiness checks
    # - Database migrations completed
    # - Redis connection established
    # - NATS connection established
    # - Required services available

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
async def liveness_check() -> Dict[str, str]:
    """
    Simple liveness check for Kubernetes probes
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }