"""
Application Settings using Pydantic Settings
"""

from typing import List, Optional
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Service Information
    SERVICE_NAME: str = "platform-api"
    SERVICE_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", description="Environment (development, staging, production)")

    # Debug & Logging
    DEBUG: bool = Field(default=False, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://dcoder:localdev@localhost:5432/dcoder_platform",
        description="PostgreSQL connection URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=40, description="Maximum overflow connections")
    DATABASE_POOL_TIMEOUT: int = Field(default=30, description="Pool timeout in seconds")

    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    REDIS_POOL_SIZE: int = Field(default=10, description="Redis connection pool size")

    # Authentication
    JWT_SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT secret key for token signing"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiration in minutes")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiration in days")

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
        description="Allowed CORS origins"
    )

    # Multi-tenancy
    TENANT_ISOLATION: str = Field(
        default="database_per_tenant",
        description="Tenant isolation strategy"
    )
    MAX_TENANTS: int = Field(default=1000, description="Maximum number of tenants")

    # Feature Flags
    FLAGSMITH_URL: Optional[str] = Field(default=None, description="Flagsmith API URL")
    FLAGSMITH_ENVIRONMENT_KEY: Optional[str] = Field(default=None, description="Flagsmith environment key")

    # NATS
    NATS_URL: str = Field(default="nats://localhost:4222", description="NATS server URL")

    # Observability
    ENABLE_METRICS: bool = Field(default=True, description="Enable Prometheus metrics")
    ENABLE_TRACING: bool = Field(default=True, description="Enable distributed tracing")
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = Field(
        default=None,
        description="OpenTelemetry OTLP exporter endpoint"
    )

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Requests per minute")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, description="Requests per hour")

    # Security
    ENCRYPTION_KEY: str = Field(
        default="your-32-byte-encryption-key-for-aes-256",
        description="Encryption key for sensitive data"
    )
    PASSWORD_MIN_LENGTH: int = Field(default=8, description="Minimum password length")
    PASSWORD_REQUIRE_UPPERCASE: bool = Field(default=True, description="Require uppercase in passwords")
    PASSWORD_REQUIRE_LOWERCASE: bool = Field(default=True, description="Require lowercase in passwords")
    PASSWORD_REQUIRE_NUMBERS: bool = Field(default=True, description="Require numbers in passwords")
    PASSWORD_REQUIRE_SPECIAL: bool = Field(default=True, description="Require special characters in passwords")

    # External Services
    LOGTO_ENDPOINT: Optional[str] = Field(default=None, description="Logto authentication endpoint")
    KONG_ADMIN_URL: str = Field(default="http://kong:8001", description="Kong Admin API URL")

    @validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        """Ensure database URL uses asyncpg for async operations"""
        if "postgresql://" in v and "+asyncpg" not in v:
            return v.replace("postgresql://", "postgresql+asyncpg://")
        return v

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("ENCRYPTION_KEY")
    def validate_encryption_key(cls, v: str) -> str:
        """Validate encryption key length for AES-256"""
        if len(v) < 32:
            raise ValueError("Encryption key must be at least 32 characters for AES-256")
        return v


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    """
    return Settings()


# Create a global settings instance
settings = get_settings()