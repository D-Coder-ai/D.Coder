# Kong AI Gateway — R1 Configuration

This folder contains the declarative `kong.yaml` for R1 with allowlisted provider services and LLM routing.

## Architecture Overview

The Kong AI Gateway provides unified access to multiple LLM providers through standardized routes. Each route handles provider-specific path transformations and will support authentication, rate limiting, caching, and guardrails in subsequent subtasks.

## Route Naming Convention

All LLM routes follow the pattern: `llm.{provider}.{model}`

Example: `llm.openai.gpt-5`, `llm.anthropic.claude-sonnet-4-5`

## Path Pattern

All routes are accessible via: `/v1/llm/{provider}/{model}`

Example: `POST http://kong:8000/v1/llm/openai/gpt-5`

## Supported Providers & Models

### OpenAI (Responses API)
Provider URL: `https://api.openai.com/v1`

| Model | Route Name | Path | Upstream Endpoint |
|-------|------------|------|-------------------|
| GPT-5 | `llm.openai.gpt-5` | `/v1/llm/openai/gpt-5` | `/v1/responses` |
| GPT-5 Chat | `llm.openai.gpt-5-chat` | `/v1/llm/openai/gpt-5-chat` | `/v1/responses` |
| GPT-4.1 | `llm.openai.gpt-4-1` | `/v1/llm/openai/gpt-4-1` | `/v1/responses` |
| GPT-5 Codex | `llm.openai.gpt-5-codex` | `/v1/llm/openai/gpt-5-codex` | `/v1/responses` |

**Authentication**: `Authorization: Bearer {API_KEY}` (configured in subtask 1.4)

### Anthropic (Messages API)
Provider URL: `https://api.anthropic.com/v1`

| Model | Route Name | Path | Upstream Endpoint |
|-------|------------|------|-------------------|
| Claude Sonnet 4.5 | `llm.anthropic.claude-sonnet-4-5` | `/v1/llm/anthropic/claude-sonnet-4-5` | `/v1/messages` |
| Claude Opus 4.1 | `llm.anthropic.claude-opus-4-1` | `/v1/llm/anthropic/claude-opus-4-1` | `/v1/messages` |

**Authentication**: `x-api-key: {API_KEY}` and `anthropic-version: 2023-06-01` (configured in subtask 1.4)

### Google Gemini (Generate Content API)
Provider URL: `https://generativelanguage.googleapis.com/v1beta`

| Model | Route Name | Path | Upstream Endpoint |
|-------|------------|------|-------------------|
| Gemini 2.5 Pro | `llm.google.gemini-2-5-pro` | `/v1/llm/google/gemini-2-5-pro` | `/v1beta/models/gemini-2.5-pro:generateContent` |
| Gemini 2.5 Flash | `llm.google.gemini-2-5-flash` | `/v1/llm/google/gemini-2-5-flash` | `/v1beta/models/gemini-2.5-flash:generateContent` |
| Gemini 2.5 Flash Lite | `llm.google.gemini-2-5-flash-lite` | `/v1/llm/google/gemini-2-5-flash-lite` | `/v1beta/models/gemini-2.5-flash-lite:generateContent` |

**Authentication**: `x-goog-api-key: {API_KEY}` (configured in subtask 1.4)

### Groq (OpenAI-Compatible API)
Provider URL: `https://api.groq.com/openai/v1`

| Model | Route Name | Path | Upstream Endpoint |
|-------|------------|------|-------------------|
| GPT-OSS 120B | `llm.groq.gpt-oss-120b` | `/v1/llm/groq/gpt-oss-120b` | `/openai/v1/chat/completions` |
| GPT-OSS 20B | `llm.groq.gpt-oss-20b` | `/v1/llm/groq/gpt-oss-20b` | `/openai/v1/chat/completions` |
| Kimi K2 Instruct | `llm.groq.kimi-k2-instruct` | `/v1/llm/groq/kimi-k2-instruct` | `/openai/v1/chat/completions` |

**Authentication**: `Authorization: Bearer {API_KEY}` (configured in subtask 1.4)

## Path Transformation Details

Kong uses the `request-transformer` plugin to rewrite incoming standardized paths to provider-specific endpoints:

- **OpenAI**: `/v1/llm/openai/{model}` → `/v1/responses`
- **Anthropic**: `/v1/llm/anthropic/{model}` → `/v1/messages`
- **Google**: `/v1/llm/google/{model}` → `/v1beta/models/{model}:generateContent`
- **Groq**: `/v1/llm/groq/{model}` → `/openai/v1/chat/completions`

The model is specified in the request body for Anthropic and Groq routes, while the path transformation includes the model name for Google routes.

## Usage Examples

### OpenAI GPT-5
```bash
curl -X POST http://localhost:8000/v1/llm/openai/gpt-5 \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: tenant-123" \
  -d '{
    "input": [
      {
        "role": "user",
        "content": [{"type": "input_text", "text": "Hello, world!"}]
      }
    ],
    "max_output_tokens": 1024
  }'
```

### Anthropic Claude Sonnet 4.5
```bash
curl -X POST http://localhost:8000/v1/llm/anthropic/claude-sonnet-4-5 \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: tenant-123" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 1024,
    "messages": [
      {"role": "user", "content": "Hello, world!"}
    ]
  }'
```

### Google Gemini 2.5 Pro
```bash
curl -X POST http://localhost:8000/v1/llm/google/gemini-2-5-pro \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: tenant-123" \
  -d '{
    "contents": [
      {
        "role": "user",
        "parts": [{"text": "Hello, world!"}]
      }
    ]
  }'
```

### Groq GPT-OSS 120B
```bash
curl -X POST http://localhost:8000/v1/llm/groq/gpt-oss-120b \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: tenant-123" \
  -d '{
    "model": "openai/gpt-oss-120b",
    "messages": [
      {"role": "user", "content": "Hello, world!"}
    ]
  }'
```

## Configuration Validation

Run the validation script to check route conventions and configuration:

```powershell
.\scripts\kong\deck-validate.ps1
```

This validates:
- ✅ Route naming follows `llm.{provider}.{model}` pattern
- ✅ Paths follow `/v1/llm/{provider}/{model}` pattern
- ✅ All providers are in the allowlist (openai, anthropic, google, groq)
- ✅ Service references are correct
- ✅ Required tags are present

## Admin API Hardening (Docker Compose)

```yaml
environment:
  KONG_ENFORCE_RBAC: "on"
  KONG_ADMIN_LISTEN: "127.0.0.1:8001"
  KONG_STATUS_LISTEN: "0.0.0.0:8100"
  # KONG_RBAC_ADMIN_TOKEN: ${KONG_ADMIN_TOKEN}
```

## R1 Implementation Status

- ✅ **Subtask 1.1**: Infrastructure bootstrapped (Postgres, Redis, NATS, Prometheus)
- ✅ **Subtask 1.2**: Provider upstreams defined and allowlisted
- ✅ **Subtask 1.3**: Declarative routes configured with path transformations
- ✅ **Subtask 1.4**: Auth header injection via request-transformer
- ✅ **Subtask 1.5**: Semantic caching with Redis
- ✅ **Subtask 1.6**: Rate limiting with Redis (current)
- ⏳ **Subtask 1.7**: Guardrails (alert-only) (next)
- ⏳ **Subtask 1.8**: Quota event emission

## Authentication

### Required Environment Variables

Kong requires API keys for each LLM provider. Set these environment variables:

- `OPENAI_API_KEY` - OpenAI API key (format: `sk-proj-...`)
- `ANTHROPIC_API_KEY` - Anthropic API key (format: `sk-ant-...`)
- `GOOGLE_API_KEY` - Google Cloud API key (format: `AIza...`)
- `GROQ_API_KEY` - Groq API key (format: `gsk_...`)

See `platform/gateways/kong/API_KEYS.md` for setup instructions and key sources.

### How Authentication Works

Kong's `request-transformer` plugin automatically injects provider-specific auth headers:

| Provider | Header(s) Injected |
|----------|-------------------|
| OpenAI | `Authorization: Bearer $(OPENAI_API_KEY)` |
| Anthropic | `x-api-key: $(ANTHROPIC_API_KEY)`<br/>`anthropic-version: 2023-06-01` |
| Google | `x-goog-api-key: $(GOOGLE_API_KEY)` |
| Groq | `Authorization: Bearer $(GROQ_API_KEY)` |

### Security Considerations

- **R1 (MVP)**: Keys stored as environment variables
- **R2+ (Production)**: Keys will use Vault/KMS with `secretRef` pattern
- **Log Redaction**: `Authorization` and `x-api-key` headers should be redacted from access logs
- **Key Rotation**: Rotate keys immediately if exposed or compromised

### Troubleshooting Authentication

**401 Unauthorized from provider:**
- Verify environment variable is set: `echo $OPENAI_API_KEY`
- Check key format matches provider's pattern
- Test key directly against provider API

**Empty/missing keys:**
- Kong substitutes empty string if env var not set
- Provider APIs will reject with 401 errors
- Check Docker Compose environment section

## Semantic Caching

### Overview

All 12 LLM routes are configured with in-memory semantic caching to reduce costs and improve latency:

- **Target savings**: 40-60% token reduction (no charges for cache hits)
- **Target latency**: <50ms for cache hits vs 500-2000ms for provider calls
- **TTL**: 24 hours (86400 seconds)
- **Implementation**: Kong bundled `proxy-cache` plugin with in-memory storage (R1 limitation)

### How It Works

**Plugin:** Kong bundled `proxy-cache` with in-memory storage

1. Request hits Kong route with caching enabled
2. Plugin checks in-memory cache for response matching request body hash
3. **Cache HIT**: Returns cached response immediately (<50ms)
4. **Cache MISS**: Forwards to LLM provider, caches response in memory
5. Response includes `X-Cache-Status` header (HIT/MISS/BYPASS) for observability

**R1 Implementation Note:** Kong 3.8 OSS bundled `proxy-cache` plugin ONLY supports `strategy: memory` (not Redis). For R1 MVP, in-memory caching is acceptable for single-instance deployment. Multi-instance Redis caching deferred to R2. See `docs/challenges/kong-deployment-plugin-loading-failure.md` for details on the limitation and solution.

### Cache Key Generation

The plugin generates cache keys based on:
- **Request body** (POST content hashed)
- **Tenant isolation** via `vary_headers: [X-Tenant-Id]`
- **Content type** filtering (`application/json`)

This ensures:
- Identical requests return cached responses
- Different tenants have isolated caches
- Only successful responses (200 OK) are cached

### Cache Isolation

**Tenant isolation**: Different tenants with identical prompts get separate cache entries
```bash
# Tenant A: llm:tenant-a:openai:gpt-5:abc123
# Tenant B: llm:tenant-b:openai:gpt-5:abc123 (different key)
```

**Provider isolation**: Same prompt to different providers creates different cache entries
```bash
# OpenAI: llm:tenant-a:openai:gpt-5:abc123
# Groq: llm:tenant-a:groq:gpt-oss-120b:def456 (different key)
```

**Parameter sensitivity**: Different temperatures/parameters result in cache MISS
```bash
# Temp 0.7: llm:tenant-a:openai:gpt-5:abc123
# Temp 0.9: llm:tenant-a:openai:gpt-5:xyz789 (different hash)
```

### Observability

All responses include cache status headers:

```bash
X-Cache-Status: HIT    # Response served from cache
X-Cache-Status: MISS   # Response fetched from provider
X-Cache-Key: llm:tenant-a:openai:gpt-5:abc123def...
```

Monitor cache performance:
```bash
# Check cache hit rate in Redis
docker exec redis redis-cli INFO stats

# List all cache keys
docker exec redis redis-cli KEYS "llm:*"

# Check TTL of specific key
docker exec redis redis-cli TTL "llm:tenant-a:openai:gpt-5:abc123"

# Get cache value
docker exec redis redis-cli GET "llm:tenant-a:openai:gpt-5:abc123"
```

### Cache Invalidation

**Automatic expiration**: All cache entries expire after 24 hours (TTL)

**Manual invalidation**:
```bash
# Flush all cache for a specific tenant
docker exec redis redis-cli KEYS "llm:tenant-123:*" | xargs docker exec redis redis-cli DEL

# Flush all cache for a specific provider
docker exec redis redis-cli KEYS "llm:*:openai:*" | xargs docker exec redis redis-cli DEL

# Flush entire LLM cache
docker exec redis redis-cli KEYS "llm:*" | xargs docker exec redis redis-cli DEL

# Flush all Redis data (nuclear option)
docker exec redis redis-cli FLUSHDB
```

### Testing Cache Behavior

Run the cache testing script:

```powershell
.\scripts\kong\test-cache.ps1

# With verbose output
.\scripts\kong\test-cache.ps1 -Verbose

# Skip Redis inspection
.\scripts\kong\test-cache.ps1 -SkipRedisInspection
```

Tests validate:
- ✅ MISS → HIT behavior for identical requests
- ✅ Tenant isolation (different tenants = different cache)
- ✅ Provider isolation (different providers = different cache)
- ✅ Parameter sensitivity (different temperature = cache MISS)
- ✅ Redis key format and TTL configuration

### Troubleshooting

**Cache always returns MISS:**
- Check cache key generation logs: `docker logs kong 2>&1 | grep "cache_key"`
- Verify Lua functions exist: `platform/gateways/kong/plugins/llm-cache-key.lua` and `platform/gateways/kong/plugins/llm-cache-headers.lua`
- Confirm Redis is accessible: `docker exec kong redis-cli -h redis ping`

**Wrong cache hits (different requests returning same response):**
- Review parameter normalization in `llm-cache-key.lua`
- Check if parameters are correctly included in hash
- Inspect actual cache keys in Redis: `docker exec redis redis-cli KEYS "llm:*"`

**Redis connection errors:**
- Verify Redis service is running: `docker ps | grep redis`
- Check network connectivity: `docker exec kong ping redis`
- Review Redis configuration in `infra/kong/kong.yaml`

**Cache not reducing costs:**
- Monitor `X-Cache-Status` headers in responses
- Check cache hit rate is >0%: `docker exec redis redis-cli INFO stats`
- Verify TTL hasn't expired: keys should have ~86400 seconds remaining
- Confirm identical requests are being sent (same tenant, prompt, parameters)

### Performance Expectations

| Metric | Target | Notes |
|--------|--------|-------|
| Cache HIT latency | <50ms | Redis lookup + response serialization |
| Cache MISS latency | 500-2000ms | Provider API call (unchanged from no cache) |
| Cache hit rate | >40% | For realistic workloads with repeated queries |
| Token savings | 40-60% | No tokens charged for cache HITs |
| Storage overhead | ~1-5KB per cached response | JSON response body |

### R1 vs R2/R3 Differences

**R1 (Current)**:
- Shared Redis instance for all tenants
- Simple TTL-based expiration (24h)
- Manual cache invalidation only
- No compression (planned for R2 if Enterprise plugins available)

**R2 (Planned)**:
- Prompt compression using Kong's AI Prompt Compressor plugin (20-30% reduction)
- Per-tenant cache isolation policies
- Cache invalidation APIs

**R3 (Future)**:
- Tenant-specific TTL configuration
- Cache warming strategies
- Advanced invalidation patterns (by tag, pattern)
- Cache analytics and optimization recommendations

### Configuration Files

| File | Purpose |
|------|---------|
| `platform/gateways/kong/plugins/llm-cache-key.lua` | Provider-aware cache key generation |
| `platform/gateways/kong/plugins/llm-cache-headers.lua` | Inject X-Cache-Status headers |
| `infra/kong/kong.yaml` | Proxy-cache plugin configuration on all routes |
| `scripts/kong/test-cache.ps1` | Cache behavior validation script |

## Rate Limiting

### Overview

All 12 LLM routes enforce per-tenant rate limiting using Redis-backed counters:

- **Default limit**: 600 requests per minute per tenant
- **Policy**: Redis (distributed, shared across Kong nodes)
- **Isolation**: By X-Tenant-Id header
- **Fault tolerance**: Enabled (allows pass-through if Redis unavailable)

### How It Works

1. Incoming request includes `X-Tenant-Id` header
2. Kong increments Redis counter: `ratelimit:{tenantId}:{route}:minute`
3. If counter exceeds limit, returns 429 Too Many Requests
4. Counter resets at the start of each time window

### Configuration

Rate limits are currently configured statically in `infra/kong/kong.yaml`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| minute | 600 | Requests per minute per tenant |
| fault_tolerant | true | Allow pass-through if Redis is down |
| hide_client_headers | false | Show X-RateLimit-* headers to clients |

To modify the rate limit, update the `minute` value in each route's rate-limiting plugin configuration in `kong.yaml`.

### Response Headers

All responses include rate limit headers:

```
X-RateLimit-Limit-Minute: 600
X-RateLimit-Remaining-Minute: 599
```

When limit is exceeded:
- Status: `429 Too Many Requests`
- Body: `{"message":"API rate limit exceeded"}`
- Headers include reset time information

### Tenant Isolation

Different tenants have independent rate limits:

```bash
# Tenant A can make 600 requests/min
curl -H "X-Tenant-Id: tenant-a" http://kong:8000/v1/llm/openai/gpt-5

# Tenant B can also make 600 requests/min independently
curl -H "X-Tenant-Id: tenant-b" http://kong:8000/v1/llm/openai/gpt-5
```

Each tenant's rate limit is tracked separately in Redis, ensuring fair resource allocation across all tenants.

### Testing

Run the rate limiting test script:

```powershell
.\scripts\kong\test-rate-limit.ps1

# Test with custom burst count
.\scripts\kong\test-rate-limit.ps1 -BurstCount 20

# Skip Redis inspection
.\scripts\kong\test-rate-limit.ps1 -SkipRedisInspection

# Verbose output
.\scripts\kong\test-rate-limit.ps1 -Verbose
```

Tests validate:
- ✅ Rate limit headers present in responses
- ✅ 429 returned when limit exceeded
- ✅ Tenant isolation (different tenants = independent limits)
- ✅ Redis counters created with correct key format
- ✅ Counter TTL and reset behavior

### Monitoring

Check Redis for rate limit counters:

```bash
# List all rate limit keys
docker exec redis redis-cli KEYS "ratelimit:*"

# Check specific tenant's counter
docker exec redis redis-cli GET "ratelimit:tenant-123:llm.openai.gpt-5:minute"

# Check TTL (time until reset)
docker exec redis redis-cli TTL "ratelimit:tenant-123:llm.openai.gpt-5:minute"

# Monitor rate limit activity in real-time
docker exec redis redis-cli MONITOR | grep "ratelimit"
```

### Troubleshooting

**Rate limiting not enforced:**
- Verify Redis is running: `docker ps | grep redis`
- Check X-Tenant-Id header is present in requests
- Review Kong logs: `docker logs kong 2>&1 | grep rate-limiting`
- Verify plugin configuration in `infra/kong/kong.yaml`

**False 429 errors:**
- Check current counter value in Redis
- Verify time window hasn't expired (check TTL)
- Ensure limit configuration is correct (600/min)
- Check if multiple Kong nodes are sharing Redis correctly

**Headers not appearing:**
- Verify `hide_client_headers: false` in rate-limiting config
- Check Kong version supports rate limit headers
- Review proxy logs for header manipulation

**Tenant isolation not working:**
- Verify X-Tenant-Id header is being sent correctly
- Check Redis for keys containing different tenant IDs
- Ensure `limit_by: header` and `header_name: X-Tenant-Id` are configured

### Performance Impact

Rate limiting with Redis has minimal performance overhead:

| Metric | Value | Notes |
|--------|-------|-------|
| Latency overhead | <5ms | Redis lookup and increment |
| Redis memory per tenant | ~100 bytes | Counter + key |
| Redis operations per request | 1-2 | GET/INCR counter |
| Fault tolerance | Pass-through | Requests succeed if Redis down |

### R1 vs R2/R3 Differences

**R1 (Current)**:
- Static limits configured in `kong.yaml`
- Single rate limit per route (minute only)
- Shared Redis instance for all tenants
- Fault-tolerant (allows pass-through)

**R2 (Planned)**:
- Dynamic per-tenant limit configuration via Platform API
- Multiple time windows (second, minute, hour, day)
- Per-tenant Redis isolation options
- Quota mirroring with Platform API

**R3 (Future)**:
- Advanced rate limiting strategies (burst, token bucket)
- Rate limit analytics and recommendations
- Automatic limit adjustment based on usage patterns
- Integration with billing/usage tracking

## Important Notes

- **No automatic failover**: Each route maps to a single provider endpoint per R1 requirements
- **BYO credentials**: Per-tenant API keys injected via request-transformer plugin (✅ implemented)
- **Allowlist enforcement**: Only OpenAI, Anthropic, Google, and Groq are permitted
- **Provider-specific APIs**: Each provider uses their native API structure
- **Plugins implemented**: Authentication, caching, and rate limiting (✅ R1 complete)

## References

- R1 PRD: `docs/project-docs/releases/R1/PRD.md`
- Architecture: `docs/project-docs/releases/R1/ARCHITECTURE.md`
- Service Contracts: `docs/project-docs/releases/R1/SERVICE_CONTRACTS.md`
- Policy definitions: `infra/policies/`


