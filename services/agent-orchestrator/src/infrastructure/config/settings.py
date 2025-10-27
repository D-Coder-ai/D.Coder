"""
Application Settings using Pydantic Settings
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    SERVICE_NAME: str = "agent-orchestrator"
    SERVICE_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", description="Environment (development, staging, production)")
    PORT: int = Field(default=8083, description="Service port")
    DEBUG: bool = Field(default=False, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    TEMPORAL_HOST: str = Field(default="localhost:7233", description="Temporal server host")
    TEMPORAL_NAMESPACE: str = Field(default="default", description="Temporal namespace")

    NATS_URL: str = Field(default="nats://localhost:4222", description="NATS server URL")

    KONG_BASE_URL: str = Field(default="http://localhost:8000", description="Kong Gateway base URL")
    PLATFORM_API_BASE: str = Field(default="http://localhost:8000/platform/v1", description="Platform API base URL via Kong")

    LITELLM_BASE: str = Field(default="http://localhost:4000", description="LiteLLM Proxy base URL")

    REDIS_URL: str = Field(default="redis://localhost:6379/1", description="Redis connection URL for caching")

    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = Field(default=None, description="OpenTelemetry OTLP exporter endpoint")
    PROMETHEUS_PORT: int = Field(default=9091, description="Prometheus metrics port")
    ENABLE_METRICS: bool = Field(default=True, description="Enable Prometheus metrics")
    ENABLE_TRACING: bool = Field(default=True, description="Enable distributed tracing")

    JWT_SECRET_KEY: str = Field(default="dev-secret-key-change-in-production", description="JWT secret key for validation")
    LOGTO_ENDPOINT: str | None = Field(default=None, description="Logto authentication endpoint")

    FLAGSMITH_URL: str | None = Field(default=None, description="Flagsmith API URL")
    FLAGSMITH_ENVIRONMENT_KEY: str | None = Field(default=None, description="Flagsmith environment key")

    ENCRYPTION_KEY: str = Field(default="dev-32-byte-key-for-aes-256-000", description="Encryption key for sensitive data")


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance
    """
    return Settings()


settings = get_settings()
