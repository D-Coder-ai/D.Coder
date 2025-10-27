# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

**D.Coder LLM Platform** is an enterprise-grade, AI-native infrastructure for building and deploying Large Language Model applications. Currently focused on **Release 1 (R1)**.

**Key characteristics:**
- Monorepo managed with Nx + pnpm workspaces
- Macro-services architecture (services larger than microservices)
- 100% open-source stack
- Hybrid gateway architecture (Kong Gateway + LiteLLM Proxy)
- Target: 70% reduction in LLM costs through semantic caching and prompt compression

## Essential Documentation

When starting a new session, review these R1 planning documents first:
- `docs/project-docs/releases/R1/ARCHITECTURE.md` - Core architecture and service design
- `docs/project-docs/releases/R1/SERVICE_CONTRACTS.md` - API conventions and event patterns
- `docs/project-docs/releases/R1/PRD.md` - Product requirements and scope
- `docs/project-docs/releases/R1/ARCHITECTURE_ADDENDUM.md` - Additional architecture decisions

## Repository Structure

```
D.Coder/
├── services/              # 8 macro-services (FastAPI + Kong + LiteLLM)
│   ├── kong-gateway/      # Platform API gateway (Port 8000)
│   ├── litellm-proxy/     # LLM gateway with caching (Port 4000)
│   ├── platform-api/      # Multi-tenancy, auth, governance (Port 8082)
│   ├── agent-orchestrator/# Temporal + LangGraph workflows (Port 8083)
│   ├── knowledge-rag/     # RAG with pgvector (Port 8084)
│   ├── integrations/      # JIRA, Bitbucket connectors (Port 8085)
│   ├── llmops/           # Agenta + MLFlow (Port 8081)
│   └── client-apps/       # Open WebUI + dashboards
├── packages/
│   ├── python/dcoder-common/    # Shared Python utilities
│   └── typescript/dcoder-sdk/   # Platform SDK
├── infrastructure/        # Base docker-compose + configs
│   └── docker-compose.base.yml  # Core infra (Postgres, Redis, NATS, etc.)
├── tools/                 # Build scripts and utilities
└── docs/                  # All documentation
```

## Architecture Patterns

### Hybrid Gateway Design
**Client → Platform API** routes to either:
- **Kong Gateway** (Port 8000) → Platform services (Agent, RAG, Integrations, LLMOps)
- **LiteLLM Proxy** (Port 4000) → LLM providers (OpenAI, Anthropic, Google/Vertex, Groq)

Kong handles platform routing, rate limiting, and quotas. LiteLLM handles LLM-specific concerns: semantic caching (Redis), prompt compression, cost tracking, and virtual keys.

### Service Boundaries
- Services ONLY depend on `packages/`, NEVER on other services
- Cross-service communication via APIs or NATS events only
- Each service is independently versioned and deployable

### Multi-Tenancy
- R1 strategy: Database per tenant
- Tenant isolation headers: `X-Tenant-Id`, `X-Platform-Id`, `X-User-Id`
- Feature flags via Flagsmith
- Quotas enforced at LiteLLM and mirrored in Platform API

### Configuration Management
- Infrastructure orchestration: `infrastructure/docker-compose.base.yml`
- Service-specific: `services/*/docker-compose.yml` (isolated dev only)
- Kong config: Declarative YAML at `services/kong-gateway/config/kong.yml`
- Environment: `.env` file (copy from `.env.example`)

## Common Commands

### Infrastructure
```bash
make infra-up          # Start Postgres, Redis, NATS, Temporal, etc.
make infra-down        # Stop infrastructure
make infra-logs        # View infrastructure logs
make status            # Show all service statuses
```

### Full Stack Development
```bash
make dev-up            # Start everything (infrastructure + all services)
make dev-down          # Stop everything
docker-compose --profile gateways up -d   # Infra + gateways only
docker-compose --profile services up -d   # Infra + services only
```

### Service-Specific Development
```bash
make service-up SERVICE=platform-api
make service-logs SERVICE=platform-api
make service-down SERVICE=platform-api

# Alternative: cd to service and use docker-compose
cd services/platform-api
docker-compose up
```

### Testing & Building
```bash
# Test single service
pnpm nx test platform-api

# Test all affected by changes
pnpm nx affected --target=test

# Test everything
make test-all

# Build affected services
pnpm nx affected --target=build

# Build all
make build-all
```

### Linting
```bash
# Lint single service
pnpm nx lint platform-api

# Lint all
make lint-all

# Python services use ruff
cd services/platform-api
poetry run ruff check .
```

### Nx Workspace
```bash
pnpm nx graph                    # Visualize dependency graph
pnpm nx show projects --affected # Show affected services
make affected-services           # Same as above
```

### Python Services
Most services use Poetry for dependency management:
```bash
cd services/platform-api
poetry install              # Install dependencies
poetry run pytest           # Run tests
poetry run ruff check .     # Lint
poetry build                # Build package
```

### Changesets (Version Management)
```bash
pnpm changeset              # Create changeset for user-facing changes
make changeset              # Same as above
pnpm version-packages       # Update versions from changesets
```

## Development Workflow

1. **Start infrastructure:** `make infra-up`
2. **Start your service:** `make service-up SERVICE=platform-api`
3. **Make changes** - hot-reload enabled via volume mounts
4. **Test:** `pnpm nx test platform-api`
5. **Lint:** `pnpm nx lint platform-api`
6. **Create changeset** (if user-facing): `pnpm changeset`
7. **Commit** using Conventional Commits format

## Commit Message Format

Follow Conventional Commits:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`

**Example:**
```
feat(platform-api): add tenant quota enforcement

- Implement quota middleware
- Add usage tracking to Redis
- Update API documentation

Closes #123
```

## API Conventions (R1 Service Contracts)

All services follow these standards:
- **Base path:** `/v1`
- **Media type:** `application/json`
- **Required headers:** `X-Request-Id`, `X-Tenant-Id`, `X-Platform-Id`, `X-User-Id`, `X-Trace-Id`
- **Optional headers:** `Idempotency-Key`
- **Pagination:** `?limit=&cursor=`; responses include `items`, `nextCursor`
- **Error format:** `{ "error": { "code": "string", "message": "string", "details": {...} } }`

## Event Conventions (NATS JetStream)

- **Subject pattern:** `domain.action` (e.g., `quota.updated`)
- **Envelope:**
  ```json
  {
    "eventId": "uuid",
    "occurredAt": "ISO-8601",
    "tenantId": "string",
    "platformId": "string",
    "correlationId": "string",
    "actor": "string",
    "payload": {}
  }
  ```

## Kong Gateway Configuration

Kong uses **declarative configuration** at `services/kong-gateway/config/kong.yml`:
- Define services (upstream LLM providers or platform services)
- Define routes (API paths)
- Configure plugins (rate limiting, auth, transforms, caching)

**Important:** Kong config is rendered from files in `services/kong-gateway/config/`. Never edit the generated `kong.yml` directly; modify source files instead.

## LiteLLM Proxy

Configuration at `services/litellm-proxy/config/litellm_config.yaml`:
- Model definitions for all providers (OpenAI, Anthropic, Google, Groq)
- Redis caching settings (default TTL: 1 hour)
- Compression middleware (2-3x compression ratio)
- Virtual keys for multi-tenancy
- Cost-based routing strategies

**Provider API keys** must be set in `.env` file:
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AI...
GROQ_API_KEY=gsk_...
```

## Testing Patterns

### Unit Tests
Located in `tests/unit/` within each service. Use pytest for Python services.

### Integration Tests
Located in `tests/integration/`. Require Docker services running:
```bash
cd services/platform-api
docker-compose up -d
poetry run pytest tests/integration/
```

### E2E Tests
Full stack required:
```bash
docker-compose --profile full up -d
# Run E2E tests
```

## Platform-Specific Notes

### Windows Development
This codebase is developed on Windows. When suggesting terminal commands:
- Check OS before suggesting shell-specific syntax
- For third-party tools, verify Windows compatibility
- Prefer cross-platform commands where possible

### Code Style
- **Python:** PEP 8, formatted with `black`, linted with `ruff`
- **TypeScript:** Prettier for formatting, ESLint for linting
- **Line length:** 88 characters (Python), 100 characters (TypeScript)

### Branch Naming
- `feat/description` - New features
- `fix/description` - Bug fixes
- `refactor/description` - Code refactoring
- `docs/description` - Documentation updates
- `chore/description` - Maintenance tasks

## Important Constraints (R1)

- **No automatic provider failover** - manual only
- **Guardrails are alert-only** - no blocking in R1
- **Database per tenant** - tenant isolation strategy
- **SSO via Logto** - auth provider
- **Feature flags via Flagsmith** - per-tenant feature enablement
- **Supported LLM providers:** OpenAI, Anthropic, Google/Vertex, Groq
- **No local inference** - BYO LLM per tenant
- **Vector DB:** pgvector for MVP, Milvus for scale (>100M vectors)

## Key Port Assignments

- 8000: Kong Gateway (proxy)
- 8001: Kong Admin API
- 4000: LiteLLM Proxy
- 8081: LLMOps Platform (Agenta/MLFlow)
- 8082: Platform API
- 8083: Agent Orchestrator
- 8084: Knowledge & RAG Service
- 8085: Integrations Service
- 5432: PostgreSQL
- 6379: Redis
- 4222: NATS
- 7233: Temporal
- 9090: Prometheus
- 3005: Grafana
- 8088: Temporal UI
- 9000/9001: MinIO

## Observability

- **Metrics:** Prometheus (http://localhost:9090)
- **Dashboards:** Grafana (http://localhost:3005, admin/admin)
- **Tracing:** OpenTelemetry exporters configured
- **LLM Observability:** Langfuse integration in LiteLLM
- **Workflows:** Temporal UI (http://localhost:8088)

## Clean-up Commands

```bash
make clean          # Clean build artifacts and caches
make reset          # DANGER: Full reset with volume deletion (requires confirmation)
```

## Repository URL

**GitHub:** https://github.com/D-Coder-ai/D.Coder

This is the consolidated monorepo. Old separate service repositories have been deprecated and deleted.
