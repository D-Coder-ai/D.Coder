# Platform API Service

Core platform API for D.Coder - Multi-tenancy, Authentication, Quotas, and Governance.

## 🏛️ Hexagonal Architecture

This service strictly follows **Hexagonal Architecture** (Ports & Adapters):

```
src/
├── domain/              # Business logic (core hexagon)
│   ├── entities/        # Domain models (Tenant, User, Quota)
│   ├── value_objects/   # Value objects (Email, TenantId)
│   ├── services/        # Domain services
│   └── ports/          # Interface definitions
│       ├── repositories/  # Data persistence interfaces
│       └── external/     # External service interfaces
├── application/         # Use cases
│   ├── commands/        # Command handlers (CQRS)
│   ├── queries/         # Query handlers (CQRS)
│   └── dto/            # Data transfer objects
├── adapters/           # Implementations
│   ├── inbound/        # API endpoints, GraphQL
│   │   └── rest/
│   │       └── v1/
│   └── outbound/       # External services
│       ├── persistence/  # Database implementations
│       ├── auth/        # Logto/Keycloak integration
│       └── events/      # NATS event publishing
└── infrastructure/      # Framework & config
    ├── fastapi/        # FastAPI setup
    ├── config/         # Settings
    └── migrations/     # Alembic migrations
```

## 🚀 Quick Start

### Local Development

```bash
# Start dependencies
docker-compose up -d

# Install dependencies
pip install -r requirements-dev.txt

# Run migrations
alembic upgrade head

# Start service
uvicorn src.main:app --reload --port 8082
```

### Docker Development

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or use Tilt for hot-reload
tilt up
```

## 🔑 Core Features

### Multi-tenancy
- Database-per-tenant isolation (R1)
- Schema-per-tenant (future)
- Row-level security (future)
- Tenant provisioning and lifecycle management

### Authentication & Authorization
- JWT-based authentication
- ABAC with Casbin
- SSO integration (Logto/Keycloak)
- API key management per tenant

### Quota Management
- User quotas
- Request rate limiting
- Storage quotas
- LLM token usage tracking
- Budget alerts and enforcement

### Provider Management
- BYO LLM credentials per tenant
- Provider configuration (OpenAI, Anthropic, Google, Groq)
- Credential encryption and secure storage
- Provider health checks

## 📡 API Endpoints

### Health
- `GET /health` - Service health check
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe

### Authentication
- `POST /v1/auth/login` - User login
- `POST /v1/auth/logout` - User logout
- `POST /v1/auth/refresh` - Refresh tokens

### Tenants
- `GET /v1/tenants` - List tenants
- `POST /v1/tenants` - Create tenant
- `GET /v1/tenants/{id}` - Get tenant
- `PATCH /v1/tenants/{id}` - Update tenant
- `DELETE /v1/tenants/{id}` - Delete tenant

### Users
- `GET /v1/users` - List users
- `POST /v1/users` - Create user
- `GET /v1/users/{id}` - Get user
- `PATCH /v1/users/{id}` - Update user
- `DELETE /v1/users/{id}` - Delete user

### Quotas
- `GET /v1/quotas` - Get quotas
- `PUT /v1/quotas` - Update quotas
- `GET /v1/quotas/usage` - Get current usage

### Providers
- `GET /v1/providers` - List providers
- `PUT /v1/providers/{provider}` - Configure provider
- `DELETE /v1/providers/{provider}` - Remove provider
- `POST /v1/providers/{provider}/test` - Test connection

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific tests
pytest tests/unit/domain/
pytest tests/integration/
pytest tests/e2e/
```

## 🔐 Security

- JWT token authentication
- API key authentication for service-to-service
- Request signing and validation
- Encryption at rest for sensitive data
- Audit logging for all operations
- RBAC/ABAC authorization

## 📊 Observability

- **Metrics**: Prometheus metrics at `/metrics`
- **Tracing**: OpenTelemetry with Jaeger
- **Logging**: Structured JSON logging
- **Health**: Kubernetes-compatible health checks

## 🗄️ Database

### Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1
```

### Multi-tenancy Strategy (R1)

Each tenant gets a dedicated database:
- Tenant provisioning creates new database
- Connection routing based on tenant context
- Isolated backups per tenant

## 🚢 Deployment

### Environment Variables

Key environment variables (see `.env.example` for full list):
- `DATABASE_URL` - PostgreSQL connection URL
- `REDIS_URL` - Redis connection URL
- `JWT_SECRET_KEY` - JWT signing key
- `ENCRYPTION_KEY` - Data encryption key
- `LOGTO_ENDPOINT` - Logto authentication endpoint

### Docker

```bash
docker build -t dcoder/platform-api .
docker run -p 8082:8082 --env-file .env dcoder/platform-api
```

## 📚 Documentation

- [API Documentation](http://localhost:8082/docs) (when DEBUG=true)
- [ReDoc](http://localhost:8082/redoc) (when DEBUG=true)
- [OpenAPI Schema](http://localhost:8082/openapi.json)
