"""
Metrics endpoint
"""

from fastapi import APIRouter, Response

from src.infrastructure.observability.metrics import get_metrics_content

router = APIRouter()


@router.get(
    "",
    summary="Prometheus Metrics",
    description="Expose Prometheus metrics"
)
async def metrics_endpoint() -> Response:
    """
    Expose Prometheus metrics in text format
    """
    content, content_type = get_metrics_content()

    return Response(
        content=content,
        media_type=content_type
    )
