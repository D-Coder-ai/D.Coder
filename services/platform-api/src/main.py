"""
Platform API Service - Main Application Entry Point
Following Hexagonal Architecture principles
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from src.infrastructure.config.settings import settings
from src.infrastructure.fastapi.middleware.logging import LoggingMiddleware
from src.infrastructure.fastapi.middleware.metrics import MetricsMiddleware
from src.infrastructure.fastapi.middleware.tenant import TenantMiddleware
from src.adapters.inbound.rest.v1 import (
    health,
    tenants,
    auth,
    quotas,
    providers,
    users
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager for startup and shutdown events
    """
    # Startup
    print(f"Starting {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")

    # Initialize database connections
    # await init_database()

    # Initialize Redis
    # await init_redis()

    # Initialize NATS
    # await init_nats()

    yield

    # Shutdown
    print(f"Shutting down {settings.SERVICE_NAME}")

    # Close database connections
    # await close_database()

    # Close Redis
    # await close_redis()

    # Close NATS
    # await close_nats()


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application
    """
    app = FastAPI(
        title=settings.SERVICE_NAME,
        description="D.Coder Platform API - Multi-tenancy, Authentication, Quotas, and Governance",
        version=settings.SERVICE_VERSION,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan
    )

    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(TenantMiddleware)

    # Include routers
    app.include_router(
        health.router,
        prefix="/health",
        tags=["health"]
    )

    app.include_router(
        auth.router,
        prefix="/v1/auth",
        tags=["authentication"]
    )

    app.include_router(
        tenants.router,
        prefix="/v1/tenants",
        tags=["tenants"]
    )

    app.include_router(
        users.router,
        prefix="/v1/users",
        tags=["users"]
    )

    app.include_router(
        quotas.router,
        prefix="/v1/quotas",
        tags=["quotas"]
    )

    app.include_router(
        providers.router,
        prefix="/v1/providers",
        tags=["providers"]
    )

    return app


# Create the application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8082,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )