# D.Coder Platform - Validation Guide

This document provides setup instructions, validation steps, and test procedures for all D.Coder platform components. Each section corresponds to a service or component and should be kept up-to-date whenever changes are made.

**Last Updated**: 2025-10-28

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Infrastructure](#infrastructure)
- [Kong Gateway](#kong-gateway)
- [LiteLLM Proxy](#litellm-proxy)
- [Platform API](#platform-api)
- [Agent Orchestrator](#agent-orchestrator)
- [Knowledge & RAG](#knowledge--rag)
- [Integrations](#integrations)
- [LLMOps](#llmops)
- [Client Apps](#client-apps)

---

## Prerequisites

### Required Tools

- Docker Desktop 24.0+ (Windows/Mac) or Docker Engine 24.0+ (Linux)
- Docker Compose 2.20+
- Git 2.40+
- Make (GNU Make 4.0+)
- pnpm 8.0+ (for Nx workspace commands)

### Optional Tools

- `yq` - YAML processor for configuration validation
- `jq` - JSON processor for API response parsing
- `curl` or `httpie` - HTTP client for testing
- `redis-cli` - Redis command-line tool for debugging
- `postgresql-client` - PostgreSQL client for database inspection

### Environment Setup

1. **Clone Repository**:
   ```bash
   git clone https://github.com/D-Coder-ai/D.Coder.git
   cd D.Coder
   ```

2. **Copy Environment File**:
   ```bash
   cp .env.example .env
   ```

3. **Configure Environment Variables**:
   Edit `.env` and set required values:
   ```bash
   # Database
   POSTGRES_USER=dcoder
   POSTGRES_PASSWORD=<secure-password>
   POSTGRES_DB=dcoder_platform

   # Redis
   REDIS_PASSWORD=<secure-password>

   # MinIO
   MINIO_ROOT_USER=minioadmin
   MINIO_ROOT_PASSWORD=<secure-password>

   # LiteLLM Proxy Configuration
   LITELLM_MASTER_KEY=sk-1234567890abcdef  # Master key for virtual key management
   DATABASE_URL=postgresql://dcoder:<password>@postgres:5432/litellm

   # LLM Provider API Keys (for LiteLLM Proxy)
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-ant-...
   GOOGLE_API_KEY=AI...
   GROQ_API_KEY=gsk_...
   ```

---

## Infrastructure

Base infrastructure services required by all platform components.

### Components

- PostgreSQL 16.2 (Port 5432)
- Redis 7.2 (Port 6379)
- MinIO S3 (Ports 9000/9001)
- NATS JetStream (Port 4222)
- Temporal Server (Port 7233)
- Temporal UI (Port 8088)

### Setup

```bash
# Start all infrastructure services
make infra-up

# Or using docker-compose directly
cd infrastructure
docker-compose -f docker-compose.base.yml up -d
```

### Validation Steps

#### 1. Verify All Services Running

```bash
# Check container status
docker-compose -f infrastructure/docker-compose.base.yml ps

# Expected: All services should show "healthy" or "running"
```

#### 2. PostgreSQL Health Check

```bash
# Test PostgreSQL connection
docker exec dcoder-postgres pg_isready -U dcoder

# Expected output: "dcoder-postgres:5432 - accepting connections"

# Connect to database
docker exec -it dcoder-postgres psql -U dcoder -d dcoder_platform

# Run test query
SELECT version();

# Expected: PostgreSQL version information
```

#### 3. Redis Health Check

```bash
# Test Redis connection
docker exec dcoder-redis redis-cli ping

# Expected output: "PONG"

# Check Redis info
docker exec dcoder-redis redis-cli info server

# Expected: Redis version and server information
```

#### 4. MinIO Health Check

```bash
# Access MinIO Console
open http://localhost:9001

# Login with credentials from .env
# Expected: MinIO dashboard loads successfully

# Test MinIO API
curl http://localhost:9000/minio/health/live

# Expected: Empty 200 OK response
```

#### 5. NATS Health Check

```bash
# Check NATS server status
curl http://localhost:8222/healthz

# Expected: Empty 200 OK response

# View NATS connections
curl http://localhost:8222/connz

# Expected: JSON with connection information
```

#### 6. Temporal Health Check

```bash
# Check Temporal server health
docker exec dcoder-temporal tctl cluster health

# Expected: "SERVING"

# Access Temporal UI
open http://localhost:8088

# Expected: Temporal UI dashboard loads
```

### Troubleshooting

**PostgreSQL won't start**:
```bash
# Check logs
docker logs dcoder-postgres

# Common fix: Remove data volume and restart
docker-compose -f infrastructure/docker-compose.base.yml down -v
make infra-up
```

**Redis connection refused**:
```bash
# Check Redis logs
docker logs dcoder-redis

# Verify Redis configuration
docker exec dcoder-redis cat /etc/redis/redis.conf
```

**NATS not accepting connections**:
```bash
# Check NATS logs
docker logs dcoder-nats

# Verify NATS configuration
docker exec dcoder-nats cat /etc/nats/nats.conf
```

---

## Kong Gateway

API Gateway for routing platform service requests with JWT authentication, rate limiting, and quota enforcement.

### Components

- Kong Gateway OSS 3.8+ (Ports 8000, 8001)
- Redis (shared from infrastructure)
- Quota Sync Sidecar (NATS → Redis)

### Setup

**Prerequisites**: Infrastructure must be running (`make infra-up`)

```bash
# Navigate to kong-gateway directory
cd services/kong-gateway

# Build Kong configuration from modular files
bash scripts/build-kong-config.sh

# Expected output: "✓ Kong configuration built successfully"

# Start Kong Gateway services
docker-compose up -d

# Wait for services to be healthy (30-60 seconds)
docker-compose ps
```

### Validation Steps

#### 1. Verify Kong Gateway Status

```bash
# Check Kong health
curl -i http://localhost:8001/status

# Expected: 200 OK with JSON status
# {
#   "database": { "reachable": true },
#   "memory": { ... },
#   "server": { "total_requests": 0, ... }
# }
```

#### 2. Verify Kong Configuration Loaded

```bash
# List all services
curl http://localhost:8001/services | jq '.data[] | {name, url}'

# Expected: 4 platform services
# - agent-orchestrator (http://agent-orchestrator:8083)
# - knowledge-rag (http://knowledge-rag:8084)
# - integrations (http://integrations:8085)
# - llmops (http://llmops:8081)

# List all routes
curl http://localhost:8001/routes | jq '.data[] | {name, paths}'

# Expected: 15+ routes with /v1/* paths

# List all plugins
curl http://localhost:8001/plugins | jq '.data[] | {name, enabled}'

# Expected: Global plugins (correlation-id, prometheus, request-id, cors)
#           Route plugins (rate-limiting, jwt, request-transformer)
```

#### 3. Verify Network Connectivity

```bash
# Check Kong is on dcoder-network
docker network inspect dcoder-network | jq '.[0].Containers | with_entries(select(.value.Name | contains("kong")))'

# Expected: kong and quota-sync containers listed

# Test Redis connectivity from Kong
docker exec kong-kong redis-cli -h redis ping

# Expected: "PONG"
```

#### 4. Verify Quota Sync Sidecar

```bash
# Check quota-sync service status
docker-compose ps quota-sync

# Expected: "running" with healthy status

# Check quota-sync logs for NATS connection
docker-compose logs quota-sync | grep -i "connected"

# Expected: "Connected to NATS at nats://nats:4222"

# Verify quota-sync can reach Redis
docker exec kong-quota-sync redis-cli -h redis ping

# Expected: "PONG"
```

#### 5. Test Route Accessibility (Without Auth)

```bash
# Test health endpoint (no auth required)
curl -i http://localhost:8000/health

# Expected: 404 (route not configured) or upstream service response

# Test protected route without JWT (should fail)
curl -i http://localhost:8000/v1/workflows

# Expected: 401 Unauthorized
# {
#   "message": "Unauthorized"
# }
```

#### 6. Verify Rate Limiting Plugin

```bash
# Make rapid requests to trigger rate limit
for i in {1..10}; do
  curl -i -H "X-Tenant-Id: test-tenant" http://localhost:8000/v1/workflows 2>&1 | grep -E "HTTP/|X-RateLimit"
done

# Expected: First requests succeed, then 429 Too Many Requests
# Response headers include:
# X-RateLimit-Limit-Minute: 1000
# X-RateLimit-Remaining-Minute: 999
# RateLimit-Reset: <timestamp>
```

#### 7. Verify Custom Quota Mirror Plugin

```bash
# Check quota-mirror plugin is loaded
curl http://localhost:8001/plugins | jq '.data[] | select(.name == "quota-mirror")'

# Expected: quota-mirror plugin configuration

# Create test quota data in Redis
docker exec dcoder-redis redis-cli HSET "quota:tenant:test-tenant" \
  limit 1000 \
  used 950 \
  remaining 50 \
  period hourly \
  reset_at "$(date -u +%s)"

# Make request with tenant that has quota
curl -i -H "X-Tenant-Id: test-tenant" http://localhost:8000/v1/workflows

# Expected: Response includes quota headers
# X-Quota-Limit: 1000
# X-Quota-Used: 950
# X-Quota-Remaining: 50
# X-Quota-Period: hourly

# Check Kong logs for quota warning (if usage > 80%)
docker-compose logs kong | grep -i "quota"

# Expected: Warning log if quota usage is high
```

#### 8. Verify Prometheus Metrics

```bash
# Fetch Prometheus metrics
curl http://localhost:8001/metrics

# Expected: Metrics in Prometheus format
# kong_http_requests_total{...} 10
# kong_latency_bucket{...} 0.5
# kong_bandwidth_bytes{...} 1024

# Check for specific metrics
curl http://localhost:8001/metrics | grep kong_http_requests_total

# Expected: Request count metrics per route
```

#### 9. Test CORS Headers

```bash
# Test preflight request
curl -i -X OPTIONS http://localhost:8000/v1/workflows \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST"

# Expected: 200 OK with CORS headers
# Access-Control-Allow-Origin: http://localhost:3000
# Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
# Access-Control-Allow-Headers: ...
```

#### 10. Test Request ID Generation

```bash
# Make request and check for correlation ID
curl -i http://localhost:8000/v1/workflows

# Expected: Response headers include
# X-Kong-Request-Id: <uuid>
# Kong-Request-Id: <uuid>
```

### Integration Tests

#### Test JWT Authentication (Requires Logto Setup)

```bash
# Generate test JWT (requires Logto running)
# This is a placeholder - actual JWT generation depends on Logto configuration
TOKEN="eyJhbGc..."  # Replace with actual JWT from Logto

# Make authenticated request
curl -i http://localhost:8000/v1/workflows \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-Id: test-tenant" \
  -H "X-Platform-Id: test-platform" \
  -H "X-User-Id: test-user"

# Expected: 200 OK (if upstream service is running)
#           or 502 Bad Gateway (if upstream not running - this is expected)

# The fact that we get past 401 means JWT auth worked
```

#### Test Quota Sync from NATS Event

```bash
# Publish test quota.updated event to NATS
docker exec -it dcoder-nats nats pub quota.updated '{
  "eventId": "test-event-001",
  "occurredAt": "2025-10-28T20:00:00Z",
  "tenantId": "tenant-001",
  "platformId": "platform-001",
  "correlationId": "corr-001",
  "actor": "litellm-proxy",
  "payload": {
    "limit": 10000,
    "used": 2500,
    "remaining": 7500,
    "period": "hourly",
    "reset_at": 1730149200
  }
}'

# Check quota-sync processed the event
docker-compose logs quota-sync | tail -20

# Expected: Log showing event received and processed

# Verify quota data in Redis
docker exec dcoder-redis redis-cli HGETALL quota:tenant:tenant-001

# Expected: Redis hash with quota data
# limit: 10000
# used: 2500
# remaining: 7500
# period: hourly
# reset_at: 1730149200
```

#### Load Test Rate Limiting

```bash
# Install Apache Bench (if not available)
# apt-get install apache2-utils  # Ubuntu/Debian
# brew install httpd             # macOS

# Run load test (100 requests, 10 concurrent)
ab -n 100 -c 10 -H "X-Tenant-Id: load-test" \
  http://localhost:8000/v1/workflows

# Expected: Some requests succeed, some get 429 (rate limited)
# Check rate limiting counters in Redis
docker exec dcoder-redis redis-cli KEYS "ratelimit:*"
```

### Performance Benchmarks

Expected latency (P95) for Kong Gateway operations:

- **JWT Validation**: < 50ms
- **Rate Limit Check**: < 10ms
- **Quota Mirror Check**: < 15ms
- **Request Transform**: < 5ms
- **Total Gateway Overhead**: < 100ms

### Troubleshooting

**Kong won't start**:
```bash
# Check logs for configuration errors
docker-compose logs kong

# Validate Kong configuration
docker exec kong-kong kong config parse /etc/kong/custom/kong.yml

# Common issues:
# - Invalid YAML syntax in kong.yml
# - Missing required environment variables
# - Redis not reachable
```

**Routes not working**:
```bash
# Rebuild configuration
bash scripts/build-kong-config.sh

# Restart Kong to reload config
docker-compose restart kong

# Check route configuration
curl http://localhost:8001/routes | jq
```

**Quota sync not receiving events**:
```bash
# Check NATS connectivity
docker exec kong-quota-sync nc -zv nats 4222

# Check quota-sync logs for errors
docker-compose logs quota-sync

# Verify NATS subject exists
docker exec dcoder-nats nats stream ls
docker exec dcoder-nats nats consumer ls
```

**Rate limiting not working**:
```bash
# Check Redis connectivity from Kong
docker exec kong-kong redis-cli -h redis ping

# Check rate limiting plugin configuration
curl http://localhost:8001/plugins | jq '.data[] | select(.name == "rate-limiting")'

# Check Redis for rate limit keys
docker exec dcoder-redis redis-cli KEYS "ratelimit:*"
```

**Custom plugin not loading**:
```bash
# Verify plugin files exist in container
docker exec kong-kong ls -la /usr/local/share/lua/5.1/kong/plugins/quota-mirror/

# Expected: handler.lua and schema.lua

# Check KONG_PLUGINS environment variable
docker exec kong-kong env | grep KONG_PLUGINS

# Expected: KONG_PLUGINS=bundled,quota-mirror

# Check plugin is loaded
curl http://localhost:8001/plugins/enabled

# Expected: quota-mirror in the list
```

### Clean Up

```bash
# Stop Kong Gateway services
docker-compose down

# Remove volumes (optional - deletes Redis data)
docker-compose down -v

# Remove generated config (optional)
rm config/kong.yml
```

---

## LiteLLM Proxy

LLM Gateway providing multi-provider routing, semantic caching, virtual keys, prompt compression, and observability for all LLM interactions.

### Components

- LiteLLM Proxy (Port 4000)
- Redis (semantic cache storage)
- PostgreSQL (virtual keys and usage tracking)
- Langfuse integration (optional observability)
- Prometheus metrics endpoint

### Setup

**Prerequisites**: Infrastructure must be running (`make infra-up`)

```bash
# Navigate to litellm-proxy directory
cd services/litellm-proxy

# Ensure provider API keys are set in .env
# OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, GROQ_API_KEY

# Start LiteLLM Proxy service
docker-compose up -d

# Wait for service to be healthy (30-40 seconds for database migrations)
docker-compose ps
```

### Validation Steps

#### 1. Verify LiteLLM Proxy Status

```bash
# Check health endpoint
curl -i http://localhost:4000/health

# Expected: 200 OK
# {
#   "status": "healthy",
#   "version": "1.x.x",
#   "uptime": "<seconds>"
# }

# Alternatively using /health/readiness
curl http://localhost:4000/health/readiness

# Expected: "success"
```

#### 2. Verify Database and Redis Connectivity

```bash
# Check LiteLLM logs for successful connections
docker-compose logs litellm-proxy | grep -i "connected\|database"

# Expected logs:
# - "Connected to database: postgresql://..."
# - "Connected to Redis: redis:6379"
# - "Database migrations completed"

# Verify LiteLLM tables were created
docker exec dcoder-postgres psql -U dcoder -d litellm -c "\dt"

# Expected tables:
# - LiteLLM_VerificationToken (virtual keys)
# - LiteLLM_SpendLogs (usage tracking)
# - LiteLLM_UserTable (user management)
# - LiteLLM_TeamTable (team/tenant management)
```

#### 3. Verify Semantic Caching Configuration

```bash
# Check Redis connection from LiteLLM container
docker exec dcoder-litellm-proxy redis-cli -h redis ping

# Expected: "PONG"

# Check Redis for semantic cache namespace
docker exec dcoder-redis redis-cli KEYS "litellm:cache:*"

# Expected: Empty initially, or existing cache keys if tests have run

# Verify embedding model for semantic caching is accessible
curl http://localhost:4000/v1/models \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" | jq '.data[] | select(.id | contains("embedding"))'

# Expected: text-embedding-ada-002 or configured embedding model
```

#### 4. Test Virtual Key Generation

```bash
# Generate a test virtual key with master key
curl -X POST http://localhost:4000/key/generate \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-001",
    "team_id": "test-tenant-001",
    "max_budget": 100.0,
    "models": ["gpt-4o-mini", "claude-haiku-3-5", "gemini-2-5-flash"],
    "duration": "30d",
    "aliases": {"gpt-4o-mini": "fast-model"}
  }'

# Expected: 200 OK
# {
#   "key": "sk-...",
#   "expires": "2025-11-28T00:00:00Z",
#   "user_id": "test-user-001",
#   "team_id": "test-tenant-001",
#   "max_budget": 100.0,
#   "models": ["gpt-4o-mini", "claude-haiku-3-5", "gemini-2-5-flash"]
# }

# Save the generated key for later tests
export TEST_VIRTUAL_KEY="sk-..."
```

#### 5. Test Provider Routing (All 4 Providers)

```bash
# Test OpenAI routing
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $TEST_VIRTUAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Say OK"}],
    "max_tokens": 5
  }'

# Expected: 200 OK with OpenAI response
# {
#   "id": "chatcmpl-...",
#   "model": "gpt-4o-mini",
#   "choices": [{"message": {"content": "OK"}}],
#   "usage": {"total_tokens": 10}
# }

# Test Anthropic routing
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $TEST_VIRTUAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-haiku-3-5",
    "messages": [{"role": "user", "content": "Say OK"}],
    "max_tokens": 5
  }'

# Expected: 200 OK with Anthropic response

# Test Google Gemini routing
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $TEST_VIRTUAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2-5-flash",
    "messages": [{"role": "user", "content": "Say OK"}],
    "max_tokens": 5
  }'

# Expected: 200 OK with Gemini response

# Test Groq routing
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $TEST_VIRTUAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "groq-llama-3-3-70b",
    "messages": [{"role": "user", "content": "Say OK"}],
    "max_tokens": 5
  }'

# Expected: 200 OK with Groq response
```

#### 6. Verify Semantic Cache Hit/Miss

```bash
# Make initial request (cache MISS expected)
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $TEST_VIRTUAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "What is the capital of France?"}],
    "max_tokens": 20
  }' -w "\nTime: %{time_total}s\n"

# Expected: 200 OK, response time 1-3 seconds (API call)
# Record response content

# Make identical request (cache HIT expected)
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $TEST_VIRTUAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "What is the capital of France?"}],
    "max_tokens": 20
  }' -w "\nTime: %{time_total}s\n"

# Expected: 200 OK, response time <100ms (cache hit)
# Response content should match first request

# Test semantic similarity (should also hit cache with 0.8 similarity threshold)
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $TEST_VIRTUAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "What is the capital city of France?"}],
    "max_tokens": 20
  }' -w "\nTime: %{time_total}s\n"

# Expected: 200 OK, fast response (semantic cache hit)

# Check Redis for cache entries
docker exec dcoder-redis redis-cli KEYS "litellm:cache:*" | head -5

# Expected: Cache keys present
```

#### 7. Test Prompt Compression Middleware

```bash
# Create large prompt (>500 tokens threshold for compression)
LARGE_PROMPT=$(python3 -c "print('This is a test context with information. ' * 100)")

curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $TEST_VIRTUAL_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"gpt-4o-mini\",
    \"messages\": [
      {\"role\": \"system\", \"content\": \"You are a helpful assistant.\"},
      {\"role\": \"user\", \"content\": \"$LARGE_PROMPT\nSummarize this.\"}
    ],
    \"max_tokens\": 50
  }"

# Expected: 200 OK, response generated
# Check logs for compression metrics

docker-compose logs litellm-proxy | grep -i "compression"

# Expected logs:
# - "Prompt compression: 850 tokens → 425 tokens (50% reduction)"
# - "Compression latency: 45ms"
```

#### 8. Verify Langfuse Observability Integration

```bash
# Make a tracked request
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $TEST_VIRTUAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello Langfuse!"}],
    "max_tokens": 10,
    "metadata": {
      "trace_name": "test-langfuse-integration",
      "user_id": "test-user-001"
    }
  }'

# Expected: 200 OK

# Check logs for Langfuse callback
docker-compose logs litellm-proxy | grep -i "langfuse"

# Expected logs:
# - "Langfuse callback: trace created"
# - "Langfuse callback: generation logged"

# If LANGFUSE_PUBLIC_KEY is configured, verify in Langfuse UI
# Navigate to: https://cloud.langfuse.com (or your instance)
# Search for trace: "test-langfuse-integration"
```

#### 9. Verify Prometheus Metrics Endpoint

```bash
# Fetch all metrics
curl http://localhost:4000/metrics

# Expected: Prometheus format metrics
# litellm_requests_total{...} 10
# litellm_request_duration_seconds_bucket{...} 0.5
# litellm_cache_hit_total{...} 5
# litellm_cache_miss_total{...} 5

# Check specific metrics
curl http://localhost:4000/metrics | grep litellm_requests_total

# Expected: Request counter with labels (model, status)

curl http://localhost:4000/metrics | grep litellm_cache

# Expected: Cache hit/miss counters
# litellm_cache_hit_total
# litellm_cache_miss_total

curl http://localhost:4000/metrics | grep litellm_compression

# Expected: Compression metrics (if compression occurred)
# litellm_compression_requests_total
# litellm_compression_savings_percent
```

#### 10. Test Rate Limiting Per Virtual Key

```bash
# Generate virtual key with low rate limit
curl -X POST http://localhost:4000/key/generate \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "rate-test-user",
    "team_id": "rate-test-tenant",
    "max_budget": 10.0,
    "models": ["gpt-4o-mini"],
    "rpm": 2
  }'

# Save the key
export RATE_LIMITED_KEY="sk-..."

# Make rapid requests to trigger rate limit
for i in {1..5}; do
  echo "Request $i:"
  curl -X POST http://localhost:4000/v1/chat/completions \
    -H "Authorization: Bearer $RATE_LIMITED_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "model": "gpt-4o-mini",
      "messages": [{"role": "user", "content": "Hi"}],
      "max_tokens": 5
    }' -w "\nStatus: %{http_code}\n\n"
  sleep 0.5
done

# Expected: First 2 requests succeed (200), then 429 Too Many Requests
# Response includes rate limit headers:
# X-RateLimit-Limit: 2
# X-RateLimit-Remaining: 0
# Retry-After: 30
```

### Integration Tests

#### Test Multi-Provider Fallback (Manual Only - No Auto-Failover in R1)

```bash
# R1 Constraint: No automatic provider failover
# Fallback must be tested manually by switching models

# Simulate provider unavailable by using invalid API key temporarily
# Then manually switch to another provider/model

# Test 1: Try primary model
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $TEST_VIRTUAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello"}]
  }'

# If fails, manually try fallback model
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $TEST_VIRTUAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-haiku-3-5",
    "messages": [{"role": "user", "content": "Hello"}]
  }'

# This validates multi-provider support without automatic failover
```

#### Test Virtual Key Budget Enforcement

```bash
# Create key with very low budget ($0.10)
curl -X POST http://localhost:4000/key/generate \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "budget-test-user",
    "team_id": "budget-test-tenant",
    "max_budget": 0.10,
    "models": ["gpt-4o-mini"]
  }'

export BUDGET_KEY="sk-..."

# Make requests until budget is exhausted
for i in {1..20}; do
  echo "Request $i:"
  curl -X POST http://localhost:4000/v1/chat/completions \
    -H "Authorization: Bearer $BUDGET_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "model": "gpt-4o-mini",
      "messages": [{"role": "user", "content": "Count to 5"}],
      "max_tokens": 20
    }' -w "\nStatus: %{http_code}\n"
done

# Expected: Eventually get 429 or 403 when budget exceeded
# Error message: "Budget exceeded for this key"

# Check key info
curl http://localhost:4000/key/info \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"key\": \"$BUDGET_KEY\"}"

# Expected: Budget usage details
# {
#   "key": "sk-...",
#   "spend": 0.12,
#   "max_budget": 0.10,
#   "budget_exceeded": true
# }
```

#### Test Streaming Support

```bash
# Test streaming with virtual key
curl -N -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $TEST_VIRTUAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Count from 1 to 5"}],
    "stream": true,
    "max_tokens": 30
  }'

# Expected: SSE stream with incremental tokens
# data: {"id":"chatcmpl-...","choices":[{"delta":{"content":"1"}}]}
# data: {"id":"chatcmpl-...","choices":[{"delta":{"content":","}}]}
# ...
# data: [DONE]
```

#### Load Test Semantic Cache Performance

```bash
# Install Apache Bench if needed
# apt-get install apache2-utils  # Ubuntu/Debian
# brew install httpd             # macOS

# Create test payload file
cat > /tmp/llm_request.json <<EOF
{
  "model": "gpt-4o-mini",
  "messages": [{"role": "user", "content": "What is 2+2?"}],
  "max_tokens": 10
}
EOF

# First run: Populate cache (1 request)
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $TEST_VIRTUAL_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/llm_request.json

# Wait for cache write
sleep 2

# Load test with cached query (100 requests, 10 concurrent)
ab -n 100 -c 10 -p /tmp/llm_request.json -T application/json \
  -H "Authorization: Bearer $TEST_VIRTUAL_KEY" \
  http://localhost:4000/v1/chat/completions

# Expected results:
# - 100% success rate (200 responses)
# - Mean response time: <100ms (all cache hits)
# - Requests per second: >100

# Compare with uncached query
cat > /tmp/llm_request_unique.json <<EOF
{
  "model": "gpt-4o-mini",
  "messages": [{"role": "user", "content": "Random: $RANDOM"}],
  "max_tokens": 10
}
EOF

# This will be slower as each request is unique (cache MISS)
```

### Performance Benchmarks

Expected performance metrics for LiteLLM Proxy operations:

- **Cache Hit Latency**: <50ms (P95)
- **Cache Miss Latency**: 500-3000ms (depends on provider)
- **Semantic Cache Match**: 80%+ similarity threshold
- **Prompt Compression Overhead**: <50ms for 1000 tokens
- **Compression Ratio**: 2-3x (50-66% reduction)
- **Virtual Key Validation**: <10ms
- **Rate Limit Check**: <5ms
- **Total Gateway Overhead**: <100ms (cache hit)

Cost Reduction Targets:
- **Semantic Caching**: 40-60% token reduction
- **Prompt Compression**: 20-30% additional savings
- **Combined Target**: 70%+ total cost reduction

### Troubleshooting

**LiteLLM won't start**:
```bash
# Check logs for errors
docker-compose logs litellm-proxy

# Common issues:
# 1. Database connection failed
docker exec dcoder-postgres pg_isready -U dcoder

# 2. Redis connection failed
docker exec dcoder-redis redis-cli ping

# 3. Invalid API keys (will start but requests fail)
docker-compose logs litellm-proxy | grep -i "authentication\|api key"

# 4. Configuration syntax error
docker exec dcoder-litellm-proxy cat /app/config/litellm_config.yaml | python -m yaml
```

**Provider requests failing**:
```bash
# Check provider API key is set
docker exec dcoder-litellm-proxy env | grep -E "OPENAI|ANTHROPIC|GOOGLE|GROQ"

# Expected: API keys present (not empty)

# Test provider directly (bypass LiteLLM)
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# If direct test fails, API key is invalid

# Check LiteLLM logs for provider errors
docker-compose logs litellm-proxy | grep -i "error\|failed"
```

**Semantic caching not working**:
```bash
# Verify Redis semantic cache keys
docker exec dcoder-redis redis-cli KEYS "litellm:cache:*"

# Check if embedding model is accessible
curl -X POST http://localhost:4000/v1/embeddings \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "text-embedding-ada-002",
    "input": "test"
  }'

# Expected: 200 OK with embeddings

# Check configuration
docker exec dcoder-litellm-proxy cat /app/config/litellm_config.yaml | grep -A 10 "cache_params"

# Verify similarity_threshold is set (0.8 default)
```

**Virtual keys not working**:
```bash
# Check database connection
docker exec dcoder-postgres psql -U dcoder -d litellm -c "SELECT * FROM \"LiteLLM_VerificationToken\" LIMIT 5;"

# Verify master key is correct
echo $LITELLM_MASTER_KEY

# Check key generation endpoint directly
curl -X POST http://localhost:4000/key/generate \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test"}' -v

# If 401: Master key is wrong
# If 500: Database issue
```

**Prompt compression not activating**:
```bash
# Compression only activates for prompts >500 tokens
# Check if prompt is large enough

# Check middleware is loaded
docker-compose logs litellm-proxy | grep -i "middleware\|compression"

# Expected: "Loaded middleware: prompt_compression_middleware"

# Verify middleware file exists
docker exec dcoder-litellm-proxy ls -la /app/middleware/

# Expected: prompt_compression.py present

# Check PYTHONPATH includes middleware
docker exec dcoder-litellm-proxy env | grep PYTHONPATH

# Expected: PYTHONPATH includes /app/middleware
```

**Prometheus metrics not available**:
```bash
# Check /metrics endpoint
curl -I http://localhost:4000/metrics

# Expected: 200 OK

# If 404, check LiteLLM version (metrics added in v1.x)
docker exec dcoder-litellm-proxy python -c "import litellm; print(litellm.__version__)"

# Check Prometheus callback is configured
docker exec dcoder-litellm-proxy cat /app/config/litellm_config.yaml | grep -i prometheus

# Expected: "success_callback: ["langfuse", "prometheus"]"
```

**High latency on cache hits**:
```bash
# Check Redis performance
docker exec dcoder-redis redis-cli --latency

# Expected: <1ms average latency

# Check Redis memory usage
docker exec dcoder-redis redis-cli INFO memory | grep used_memory_human

# If high, may need to adjust cache TTL or max memory

# Check network latency between containers
docker exec dcoder-litellm-proxy ping -c 5 dcoder-redis

# Expected: <1ms average
```

### Clean Up

```bash
# Stop LiteLLM Proxy service
docker-compose down

# Remove volumes (optional - deletes virtual keys and usage data)
docker-compose down -v

# Clear Redis cache manually (without removing volumes)
docker exec dcoder-redis redis-cli FLUSHDB
```

---

## Platform API

*To be documented when Platform API implementation is complete.*

---

## Agent Orchestrator

*To be documented when Agent Orchestrator implementation is complete.*

---

## Knowledge & RAG

*To be documented when Knowledge & RAG implementation is complete.*

---

## Integrations

*To be documented when Integrations implementation is complete.*

---

## LLMOps

*To be documented when LLMOps implementation is complete.*

---

## Client Apps

*To be documented when Client Apps implementation is complete.*

---

## Full Stack Testing

### Start All Services

```bash
# Start infrastructure
make infra-up

# Start all platform services
make dev-up

# Or start specific profiles
docker-compose --profile gateways up -d    # Infrastructure + gateways only
docker-compose --profile services up -d    # Infrastructure + services only
docker-compose --profile full up -d        # Everything
```

### End-to-End Validation

*To be documented when all services are implemented.*

---

## Appendix: Common Commands

### Docker Commands

```bash
# View all running containers
docker ps

# View logs for specific service
docker logs <container-name>

# Follow logs in real-time
docker logs -f <container-name>

# Execute command in container
docker exec -it <container-name> <command>

# View container resource usage
docker stats

# Restart specific service
docker-compose restart <service-name>
```

### Network Debugging

```bash
# Inspect network
docker network inspect dcoder-network

# Test connectivity between containers
docker exec <container1> ping <container2>

# Check DNS resolution
docker exec <container> nslookup <service-name>

# Check port listening
docker exec <container> netstat -tulpn
```

### Database Commands

```bash
# PostgreSQL
docker exec -it dcoder-postgres psql -U dcoder -d dcoder_platform

# Redis
docker exec -it dcoder-redis redis-cli

# View all Redis keys
docker exec dcoder-redis redis-cli KEYS "*"

# Monitor Redis commands
docker exec dcoder-redis redis-cli MONITOR
```

---

## Contributing to This Document

When you complete development or make updates to any component:

1. **Update the corresponding section** with setup instructions, validation steps, and tests
2. **Include actual commands** that can be copy-pasted
3. **Provide expected outputs** for each validation step
4. **Add troubleshooting** for common issues you encountered
5. **Update performance benchmarks** if applicable
6. **Test your instructions** on a clean environment before committing

This document should be a **living guide** that evolves with the platform.
