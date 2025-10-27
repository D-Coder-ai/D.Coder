"""
Agent Orchestration Service - Durable workflows with Temporal and LangGraph
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.adapters.inbound.rest.v1 import health, metrics, workflows
from src.infrastructure.config.settings import settings
from src.infrastructure.middleware.auth import AuthMiddleware
from src.infrastructure.middleware.header_propagation import HeaderPropagationMiddleware
from src.infrastructure.middleware.logging import LoggingMiddleware
from src.infrastructure.middleware.tenant import TenantMiddleware
from src.infrastructure.observability.metrics import setup_metrics
from src.infrastructure.observability.tracing import setup_tracing


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    setup_metrics()
    setup_tracing(app)

    yield


app = FastAPI(
    title=settings.SERVICE_NAME,
    description="Agent Orchestration Service - Durable workflows with Temporal and LangGraph",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(HeaderPropagationMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(TenantMiddleware)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for consistent error responses
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "internal_error",
                "message": str(exc),
                "details": {}
            }
        }
    )


app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(workflows.router, prefix="/v1/workflows", tags=["Workflows"])
app.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
