# Gateway Service

AI Gateway Service for D.Coder Platform - Kong-based LLM routing, caching, and compression.

## 🏛️ Architecture

This service follows **Hexagonal Architecture** (Ports & Adapters):

```
src/
├── domain/          # Business logic (core hexagon)
│   ├── models/      # Domain models
│   ├── services/    # Domain services
│   └── ports/       # Interface definitions
├── application/     # Use cases
│   ├── routing/     # LLM routing logic
│   ├── caching/     # Semantic caching
│   └── compression/ # Prompt compression
├── adapters/        # Implementations
│   ├── inbound/     # Kong plugins, HTTP handlers
│   └── outbound/    # External services
└── infrastructure/  # Framework & config
```

## 🚀 Quick Start

### Local Development

```bash
# Start with Docker Compose
docker-compose up -d

# Or use Tilt for hot-reload
tilt up
```

### Configuration

Kong configuration is declarative via `config/kong.yml`:
- Services: Define upstream LLM providers
- Routes: Define API paths
- Plugins: Configure rate limiting, caching, etc.

## 🔌 Features

### Core Capabilities
- **Multi-LLM Routing**: OpenAI, Anthropic, Google Vertex AI, Groq
- **Semantic Caching**: 40-60% token reduction
- **Prompt Compression**: 20-30% size reduction
- **Rate Limiting**: Per-tenant quotas
- **Observability**: Prometheus metrics, distributed tracing

### Kong Plugins Used
- `ai-proxy`: LLM provider routing
- `ai-prompt-template`: Prompt templating
- `ai-prompt-guard`: Security guardrails
- `ai-request-transformer`: Request transformation
- `ai-response-transformer`: Response transformation
- `rate-limiting`: Rate limits with Redis
- `prometheus`: Metrics collection
- `correlation-id`: Request tracing
- `http-log`: Centralized logging

## 📡 API Endpoints

### Proxy Endpoints
- `GET /health` - Health check
- `POST /v1/llm/openai/chat` - OpenAI chat completions
- `POST /v1/llm/anthropic/chat` - Anthropic messages
- `POST /v1/llm/vertex/chat` - Google Vertex AI

### Admin Endpoints
- `GET http://localhost:8001/services` - List services
- `GET http://localhost:8001/routes` - List routes
- `GET http://localhost:8001/plugins` - List plugins
- `GET http://localhost:8001/status` - Gateway status

## 🧪 Testing

```bash
# Run unit tests
pytest tests/unit

# Run integration tests
pytest tests/integration

# Run end-to-end tests
pytest tests/e2e
```

## 🔧 Development

### Adding New LLM Provider

1. Define service in `config/kong.yml`
2. Create route mapping
3. Configure provider-specific plugins
4. Add adapter in `src/adapters/outbound/llm_providers/`

### Custom Kong Plugin Development

1. Create plugin in `plugins/` directory
2. Implement handler in Lua
3. Add schema definition
4. Register in Kong configuration

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

## 📚 Documentation

- [Kong Documentation](https://docs.konghq.com/)
- [Kong AI Gateway](https://docs.konghq.com/gateway/latest/ai/)
- [Plugin Development](https://docs.konghq.com/gateway/latest/plugin-development/)

## 🔧 Admin Runbook (R1)

### Health Checks

#### Global Kong Health
```bash
# Check Kong gateway status
curl http://localhost:8000/health

# Expected: HTTP 200 with status information
```

#### Per-Service Health Checks
```bash
# Platform API
curl http://localhost:8000/v1/platform-api/health

# Agent Orchestrator
curl http://localhost:8000/v1/agent-orchestrator/health

# Knowledge & RAG
curl http://localhost:8000/v1/knowledge-rag/health

# Integrations
curl http://localhost:8000/v1/integrations/health

# LLMOps
curl http://localhost:8000/v1/llmops/health
```

### Admin API Usage

#### List All Services
```bash
curl http://localhost:8001/services | jq
```

#### List All Routes
```bash
curl http://localhost:8001/routes | jq
```

#### List All Plugins
```bash
# Global plugins
curl http://localhost:8001/plugins | jq

# Plugins for specific route
curl http://localhost:8001/routes/{route-id}/plugins | jq
```

#### Gateway Status
```bash
# Detailed Kong status
curl http://localhost:8001/status | jq

# Example response includes:
# - database: connection status
# - server: Kong server info
# - memory: memory usage
```

### Rate Limit Verification

#### Check Rate Limit Headers
```bash
# Make request with tenant ID
curl -i http://localhost:8000/v1/tenants \
  -H "X-Tenant-Id: test-tenant-123"

# Look for these headers in response:
# X-RateLimit-Limit-Minute: 1000
# X-RateLimit-Remaining-Minute: 999
```

#### Verify Redis Connection
```bash
# Check Redis is accessible to Kong
docker-compose exec redis redis-cli ping
# Expected: PONG

# Check rate limit keys in Redis
docker-compose exec redis redis-cli --scan --pattern "ratelimit:*"
```

#### Test Rate Limit Enforcement
```bash
# Rapid requests to trigger rate limit (adjust loop count based on limit)
for i in {1..1005}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -H "X-Tenant-Id: test-tenant" \
    http://localhost:8000/v1/tenants
done

# Expected: First 1000 return 4xx/5xx (upstream dependent), then 429 (Too Many Requests)
```

### Metrics & Observability

#### Prometheus Metrics Endpoint
```bash
# Get all Kong metrics
curl http://localhost:8001/metrics

# Filter specific metrics
curl http://localhost:8001/metrics | grep kong_http_requests_total
curl http://localhost:8001/metrics | grep kong_latency
curl http://localhost:8001/metrics | grep kong_bandwidth
```

#### Key Metrics to Monitor
- `kong_http_requests_total`: Total HTTP requests by service/route
- `kong_latency_ms_bucket`: Request latency histogram
- `kong_bandwidth_bytes`: Bandwidth usage
- `kong_datastore_reachable`: Database/Redis connectivity (0 or 1)
- `kong_nginx_http_current_connections`: Active connections

#### Correlation & Request Tracing
```bash
# Verify correlation headers are added
curl -i http://localhost:8000/v1/tenants \
  -H "X-Tenant-Id: test-tenant"

# Look for:
# X-Correlation-ID: <uuid>
# X-Request-ID: <uuid>
```

### Common Troubleshooting

#### Kong Won't Start
```bash
# Check logs
docker-compose logs kong

# Validate configuration
docker run --rm -v $(pwd)/config:/config kong:3.8 \
  kong config parse /config/kong.yml

# Check dependencies
docker-compose ps redis  # Should be "Up"
```

#### Route Not Found (404)
```bash
# Verify route exists
curl http://localhost:8001/routes | jq '.data[] | {name, paths}'

# Check service upstream
curl http://localhost:8001/services/{service-name} | jq '.host, .port'

# Test upstream directly (outside Kong)
curl http://{upstream-host}:{port}/health
```

#### Rate Limiting Not Working
```bash
# Verify rate-limiting plugin is active
curl http://localhost:8001/plugins | jq '.data[] | select(.name=="rate-limiting")'

# Check Redis connectivity
docker-compose exec kong ping redis -c 1

# Verify tenant header is sent
curl -i http://localhost:8000/v1/tenants \
  -H "X-Tenant-Id: your-tenant-id" \
  | grep -i "x-ratelimit"
```

#### Metrics Not Available
```bash
# Check Prometheus plugin is enabled
curl http://localhost:8001/plugins | jq '.data[] | select(.name=="prometheus")'

# Verify metrics endpoint
curl -I http://localhost:8001/metrics

# Check Kong status
curl http://localhost:8001/status | jq '.server'
```

#### Header Propagation Issues
```bash
# Test header injection
curl -v http://localhost:8000/v1/tenants 2>&1 | grep -i "x-request-id\|x-correlation-id"

# Check global plugins
curl http://localhost:8001/plugins | jq '.data[] | select(.name | contains("id"))'
```

### Configuration Reload (DB-less Mode)

Kong is running in DB-less mode. To update configuration:

```bash
# 1. Edit config files
vim config/kong.yml
vim config/routes/platform-services.yml

# 2. Rebuild and restart
docker-compose down
docker-compose up --build -d

# 3. Verify new config loaded
docker-compose logs kong | grep "declarative config"
curl http://localhost:8001/routes | jq '.data | length'
```

### Backup & Recovery

#### Export Current Configuration
```bash
# Backup merged config
docker-compose exec kong cat /tmp/kong-merged.yaml > backup-$(date +%Y%m%d).yaml

# Backup individual configs
cp config/kong.yml config/kong.yml.backup
cp config/routes/platform-services.yml config/routes/platform-services.yml.backup
cp config/routes/health.yml config/routes/health.yml.backup
```

#### Restore Configuration
```bash
# Restore from backup
cp backup-20241027.yaml config/kong.yml

# Restart Kong
docker-compose restart kong
```

### Performance Tuning

#### Connection Pooling
```bash
# Check current connections
curl http://localhost:8001/status | jq '.server.connections_active'

# Adjust in docker-compose.yml or Dockerfile if needed
# KONG_NGINX_HTTP_UPSTREAM_KEEPALIVE=60
```

#### Cache Hit Rates
```bash
# Monitor proxy-cache plugin hits
curl http://localhost:8001/metrics | grep kong_cache
```

### Security Checklist

- [ ] API keys not hardcoded in config files
- [ ] `.env` file not committed to version control
- [ ] Rate limits configured per tenant
- [ ] Correlation IDs enabled for audit trails
- [ ] Admin API not exposed publicly (8001 internal only)
- [ ] SSL certificates configured for production (8443, 8444)