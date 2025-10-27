# Kong Gateway Service

Platform API Gateway for D.Coder - Routes traffic to platform services (Agent Orchestrator, Knowledge & RAG, Integrations, LLMOps) with JWT authentication, rate limiting, and quota mirroring.

## 🏛️ Architecture Overview

Kong Gateway (Port 8000) serves as the primary API gateway for D.Coder platform services, providing:

- **Service Routing**: Routes to Agent Orchestrator (8083), Knowledge & RAG (8084), Integrations (8085), LLMOps (8081)
- **Authentication**: JWT validation from Logto (OIDC provider)
- **Rate Limiting**: Redis-backed distributed rate limiting per tenant
- **Quota Mirroring**: Syncs quota data from LiteLLM via NATS events
- **Observability**: Prometheus metrics, correlation IDs, distributed tracing
- **Request Transformation**: Injects required R1 service contract headers

**Note**: LiteLLM Proxy (Port 4000) handles LLM provider traffic separately. See hybrid gateway architecture in ARCHITECTURE.md.

## 📂 Directory Structure

```
services/kong-gateway/
├── config/
│   ├── services/           # Service definitions (upstreams)
│   │   ├── agent-orchestrator.yml
│   │   ├── knowledge-rag.yml
│   │   ├── integrations.yml
│   │   └── llmops.yml
│   ├── routes/             # Route definitions
│   │   ├── agent-routes.yml
│   │   ├── rag-routes.yml
│   │   ├── integration-routes.yml
│   │   └── llmops-routes.yml
│   ├── plugins/            # Plugin configurations
│   │   ├── global-plugins.yml
│   │   ├── rate-limiting.yml
│   │   ├── jwt-auth.yml
│   │   └── request-transform.yml
│   └── kong.yml            # Generated declarative config (DO NOT EDIT)
├── plugins/                # Custom Lua plugins
│   └── quota-mirror/       # Quota mirroring plugin
│       ├── handler.lua
│       └── schema.lua
├── src/
│   └── quota-sync/         # Quota sync sidecar
│       ├── sync.py
│       ├── requirements.txt
│       └── Dockerfile
├── scripts/
│   └── build-kong-config.sh  # Build script for kong.yml
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Redis (for rate limiting and quota cache)
- PostgreSQL (for Kong database)
- NATS JetStream (for quota events)
- Platform services running (Agent, RAG, Integrations, LLMOps)

### Local Development

```bash
# 1. Build Kong configuration from modular files
./scripts/build-kong-config.sh

# 2. Start Kong Gateway with dependencies
docker-compose up -d

# 3. Verify services are running
docker-compose ps

# 4. Check Kong health
curl http://localhost:8001/status
```

### Modular Configuration System

Kong configuration uses a **modular approach** for maintainability:

1. **Edit source files** in `config/services/`, `config/routes/`, or `config/plugins/`
2. **Run build script** to generate `config/kong.yml`:
   ```bash
   ./scripts/build-kong-config.sh
   ```
3. **Reload Kong** to apply changes:
   ```bash
   docker-compose restart kong
   # OR via Admin API:
   curl -X POST http://localhost:8001/config -F config=@config/kong.yml
   ```

**Important**: Never edit `config/kong.yml` directly - it's auto-generated!

## 🔌 Features

### Core Capabilities
- **Platform Service Routing**: Agent Orchestrator, Knowledge & RAG, Integrations, LLMOps
- **JWT Authentication**: Validates JWTs from Logto (OIDC provider)
- **Rate Limiting**: Redis-backed distributed rate limiting per tenant (via X-Tenant-Id header)
- **Quota Mirroring**: Syncs quota usage from LiteLLM via NATS events (alert-only in R1)
- **Request Transformation**: Injects R1 service contract headers (X-Request-Id, X-Tenant-Id, etc.)
- **Observability**: Prometheus metrics, correlation IDs, distributed tracing

### Kong OSS Plugins Used

**All plugins are Kong OSS (no Enterprise dependencies)**:

- `jwt`: JWT authentication and validation
- `rate-limiting`: Redis-backed rate limiting per tenant
- `request-transformer`: Add/remove/modify request headers
- `correlation-id`: Generate unique request IDs
- `prometheus`: Export metrics for monitoring
- `request-id`: Request ID propagation
- `cors`: Cross-origin resource sharing

### Custom Plugins

- `quota-mirror`: Custom Lua plugin for quota mirroring from LiteLLM (alert-only in R1)

## 📡 API Endpoints

### Platform Service Routes (Port 8000)

**Agent Orchestrator**:
- `GET/POST/PUT/DELETE /v1/workflows` - Workflow management
- `GET/POST/PUT/DELETE /v1/agents` - Agent management
- `GET/POST /v1/executions` - Execution tracking

**Knowledge & RAG**:
- `GET/POST/PUT/DELETE /v1/knowledge/documents` - Document management
- `POST /v1/knowledge/search` - Semantic search
- `POST /v1/rag` - RAG pipeline
- `GET/POST/PUT/DELETE /v1/knowledge/collections` - Collection management

**Integrations**:
- `GET/POST/PUT/DELETE /v1/integrations` - Integration management
- `GET/POST/PUT /v1/integrations/jira` - JIRA integration
- `GET/POST/PUT /v1/integrations/bitbucket` - Bitbucket integration
- `POST /v1/integrations/webhooks` - Webhook handling

**LLMOps**:
- `GET/POST/PUT/DELETE /v1/llmops/experiments` - Experiment management
- `GET/POST/PUT/DELETE /v1/llmops/prompts` - Prompt management
- `GET/POST /v1/llmops/evaluations` - Evaluation tracking
- `GET/POST/PUT /v1/llmops/deployments` - Deployment management

### Admin Endpoints (Port 8001)
- `GET http://localhost:8001/services` - List configured services
- `GET http://localhost:8001/routes` - List configured routes
- `GET http://localhost:8001/plugins` - List active plugins
- `GET http://localhost:8001/status` - Gateway health status
- `GET http://localhost:8001/metrics` - Prometheus metrics
- `POST http://localhost:8001/config` - Reload declarative config

### Required Headers (R1 Service Contracts)

All platform API requests must include:
- `Authorization: Bearer <jwt>` - JWT from Logto
- `X-Tenant-Id: <tenant-id>` - Tenant identifier (for rate limiting)
- `X-Platform-Id: <platform-id>` - Platform identifier
- `X-User-Id: <user-id>` - User identifier

Optional headers:
- `X-Request-Id: <uuid>` - Auto-generated if not provided
- `X-Trace-Id: <uuid>` - For distributed tracing
- `Idempotency-Key: <key>` - For idempotent requests

## 🧪 Testing

### Manual Testing

```bash
# Test Kong health
curl http://localhost:8001/status

# Test platform service routing (requires JWT)
curl -X GET http://localhost:8000/v1/workflows \
  -H "Authorization: Bearer <your-jwt>" \
  -H "X-Tenant-Id: tenant-123" \
  -H "X-Platform-Id: platform-1" \
  -H "X-User-Id: user-456"

# Test rate limiting (should return 429 after limit)
for i in {1..150}; do
  curl -X GET http://localhost:8000/v1/workflows \
    -H "Authorization: Bearer <jwt>" \
    -H "X-Tenant-Id: tenant-123"
done

# Check Prometheus metrics
curl http://localhost:8001/metrics
```

### Integration Tests

```bash
# Run integration tests (coming soon)
pytest tests/integration

# Test JWT validation
pytest tests/integration/test_jwt_auth.py

# Test rate limiting
pytest tests/integration/test_rate_limiting.py

# Test quota mirroring
pytest tests/integration/test_quota_mirror.py
```

## 🔧 Development

### Adding New Platform Service

1. **Create service definition**:
   ```bash
   # Create config/services/my-service.yml
   - name: my-service
     url: http://my-service:8086
     protocol: http
     connect_timeout: 60000
     write_timeout: 60000
     read_timeout: 60000
     retries: 3
   ```

2. **Create route definitions**:
   ```bash
   # Create config/routes/my-service-routes.yml
   routes:
     - name: my-service-api
       service: my-service
       paths:
         - /v1/my-service
       methods:
         - GET
         - POST
   ```

3. **Rebuild configuration**:
   ```bash
   ./scripts/build-kong-config.sh
   docker-compose restart kong
   ```

### Custom Kong Plugin Development

1. Create plugin directory:
   ```bash
   mkdir -p plugins/my-plugin
   ```

2. Implement schema (`plugins/my-plugin/schema.lua`):
   ```lua
   return {
     name = "my-plugin",
     fields = {
       { config = {
           type = "record",
           fields = {
             { my_setting = { type = "string", required = true } },
           },
         },
       },
     },
   }
   ```

3. Implement handler (`plugins/my-plugin/handler.lua`):
   ```lua
   local BasePlugin = require "kong.plugins.base_plugin"
   local MyPluginHandler = BasePlugin:extend()

   function MyPluginHandler:access(conf)
     -- Plugin logic here
   end

   return MyPluginHandler
   ```

4. Add to Kong configuration and rebuild

### Quota Sync Sidecar

The quota-sync sidecar listens for `quota.updated` events from NATS and mirrors quota data to Redis:

- **Source**: `src/quota-sync/sync.py`
- **Purpose**: Enable quota-mirror plugin to check tenant quotas
- **Architecture**: NATS subscriber → Redis writer
- **R1 Behavior**: Alert-only (no request blocking)

## 📊 Monitoring

- **Metrics**: http://localhost:8001/metrics (Prometheus format)
- **Health**: http://localhost:8001/status
- **Admin API**: http://localhost:8001

## 🔒 Security

- API key authentication per tenant
- Request/response validation
- Prompt injection prevention
- Rate limiting and quotas
- Audit logging

## 🚢 Deployment

### Docker
```bash
docker build -t dcoder/gateway .
docker run -p 8000:8000 -p 8001:8001 dcoder/gateway
```

### Environment Variables
- `KONG_DATABASE`: Database type (postgres)
- `KONG_PG_HOST`: PostgreSQL host
- `KONG_PG_USER`: PostgreSQL user
- `KONG_PG_PASSWORD`: PostgreSQL password
- `KONG_REDIS_HOST`: Redis host for caching
- `KONG_LOG_LEVEL`: Logging level

## 📊 Monitoring & Observability

### Prometheus Metrics

Kong exposes Prometheus metrics at `http://localhost:8001/metrics`:

- `kong_http_requests_total` - Total HTTP requests by service, route, status
- `kong_latency_bucket` - Request latency histograms
- `kong_bandwidth_bytes` - Bandwidth usage by service
- `kong_upstream_health` - Upstream service health checks

### Quota Monitoring

Quota metrics are available in Redis:
```bash
# Check tenant quota
redis-cli HGETALL quota:tenant:tenant-123

# Output:
# limit: 10000
# used: 4532
# remaining: 5468
# period: monthly
# reset_at: 2025-11-01T00:00:00Z
# last_updated: 2025-10-27T20:00:00Z
```

### Logging

Kong logs to stdout/stderr:
```bash
# View Kong logs
docker-compose logs -f kong

# View quota-sync logs
docker-compose logs -f quota-sync
```

## 🔒 Security

### Authentication

- **JWT Validation**: All routes require valid JWT from Logto
- **Claims Verification**: Verifies `exp`, `nbf` claims
- **Token Sources**: Authorization header, query param, or cookie

### Rate Limiting

- **Per-Tenant Limits**: Enforced via X-Tenant-Id header
- **Redis-Backed**: Distributed rate limiting across Kong instances
- **Fail-Open**: If Redis is down, requests are allowed (R1 design)

### Quota Enforcement

- **R1 Behavior**: Alert-only (no request blocking)
- **R2+ Behavior**: Configurable blocking on quota exceeded
- **Data Source**: LiteLLM quota.updated events via NATS

## 📚 Documentation

- [Kong Gateway OSS Documentation](https://docs.konghq.com/gateway/)
- [Kong Plugin Hub](https://docs.konghq.com/hub/)
- [Kong Declarative Configuration](https://docs.konghq.com/gateway/latest/production/deployment-topologies/db-less-and-declarative-config/)
- [R1 Service Contracts](../../docs/project-docs/releases/R1/SERVICE_CONTRACTS.md)
- [R1 Architecture Guide](../../docs/project-docs/releases/R1/ARCHITECTURE.md)

## 🤝 Contributing

When contributing to Kong Gateway configuration:

1. **Never edit `config/kong.yml` directly** - it's auto-generated
2. **Edit modular source files** in `config/services/`, `config/routes/`, `config/plugins/`
3. **Run build script** after changes: `./scripts/build-kong-config.sh`
4. **Test changes** locally before committing
5. **Verify all plugins are Kong OSS** (no Enterprise dependencies)
6. **Follow R1 service contracts** for headers and API patterns

## 📝 License

D.Coder Platform - Apache 2.0 License
Kong Gateway OSS - Apache 2.0 License
