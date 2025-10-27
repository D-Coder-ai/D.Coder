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

*To be documented when LiteLLM Proxy implementation is complete.*

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
