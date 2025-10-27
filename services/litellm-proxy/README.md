# LiteLLM Proxy - D.Coder R1

LiteLLM Proxy service providing specialized LLM gateway capabilities including:

- **Multi-LLM Routing**: Native support for OpenAI, Anthropic, Google Gemini, and Groq
- **Redis-Backed Semantic Caching**: 40-60% token reduction through intelligent caching
- **Prompt Compression**: 20-30% additional savings using LLMLingua
- **Simple-Shuffle Routing**: Round-robin routing (cost-based routing deferred to R2)
- **Virtual Keys**: Multi-tenancy without per-tenant database overhead
- **Observability**: Native Langfuse and Prometheus integration

## Architecture

Part of the hybrid gateway architecture:

```
Client → Platform API ─┬─→ Kong Gateway → Platform Services (Agent, RAG, etc.)
                       └─→ LiteLLM Proxy → LLM Providers
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- LLM Provider API keys (OpenAI, Anthropic, Google, Groq)
- Redis and PostgreSQL (provided by platform/docker-compose.yml)

### Configuration

1. Copy environment template:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys:
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AI...
GROQ_API_KEY=gsk_...
```

3. Start the service (from `platform/` directory):
```bash
docker-compose up -d litellm-proxy
```

### Health Check

```bash
curl http://localhost:4000/health
```

## Usage

### Direct API Calls

LiteLLM exposes an OpenAI-compatible API:

```bash
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Supported Models

**OpenAI:**
- gpt-4o, gpt-4o-mini
- gpt-4-turbo
- gpt-3.5-turbo

**Anthropic:**
- claude-sonnet-4-5
- claude-opus-4-1
- claude-haiku-3-5

**Google:**
- gemini-2-5-pro, gemini-2-5-flash
- gemini-1-5-pro

**Groq:**
- groq-llama-3-3-70b
- groq-mixtral-8x7b

## Features

### 1. Semantic Caching

**Redis-backed semantic caching** using embedding similarity matching with 1-hour TTL:

```yaml
# config/litellm_config.yaml
litellm_settings:
  cache: true
  cache_params:
    type: redis-semantic  # Embedding-based similarity matching
    host: redis
    port: 6379
    ttl: 3600  # 1 hour cache TTL
    namespace: "litellm:cache"
    similarity_threshold: 0.8  # 80% similarity required for cache hit
    redis_semantic_cache_embedding_model: "text-embedding-ada-002"
    supported_call_types: ["acompletion", "atext_completion", "aembedding"]
    max_connections: 100
```

**How It Works:**
1. **First Request (Cache MISS)**:
   - User prompt is converted to embedding using `text-embedding-ada-002`
   - Embedding stored in Redis with response
   - Full LLM API call made

2. **Subsequent Request (Cache HIT)**:
   - New prompt is converted to embedding
   - Cosine similarity calculated against cached embeddings
   - If similarity ≥ 0.8 (80%), cached response returned
   - No LLM API call needed

**Example:**
```bash
# First request - exact match
"What is the capital of France?" → MISS → API call → "Paris" (cached)

# Second request - exact match
"What is the capital of France?" → HIT → "Paris" (from cache, <50ms)

# Third request - semantic match
"What is the capital city of France?" → HIT → "Paris" (81% similarity, cached)

# Fourth request - no match
"What is the population of Paris?" → MISS → API call (59% similarity, below threshold)
```

**Benefits:**
- **40-60% token reduction** through intelligent caching
- **<50ms cache hit latency** (vs 500-3000ms for API calls)
- **Automatic cache key generation** based on embeddings
- **Tenant isolation** via namespace prefix
- **Semantic understanding** - similar questions hit cache even with different wording

**Configuration Tuning:**
- **similarity_threshold: 0.8** (default) - Higher = stricter matching, lower cache hit rate
- **similarity_threshold: 0.9** - Very strict, only nearly identical prompts hit cache
- **similarity_threshold: 0.7** - More lenient, higher cache hit rate but less precise

**Monitoring:**
```bash
# Check cache hit/miss ratio in Prometheus
curl http://localhost:4000/metrics | grep litellm_cache

# View cached embeddings in Redis
docker exec dcoder-redis redis-cli KEYS "litellm:cache:*"

# Check cache size
docker exec dcoder-redis redis-cli INFO memory | grep used_memory_human
```

### 2. Prompt Compression

LLMLingua-based compression before LLM calls:

**Configuration:**
- Default: 2x compression (50% size reduction)
- RAG queries: 3x compression (33% size)
- Minimum: 500 tokens

**Compression Metrics:**
- Original tokens
- Compressed tokens
- Savings percentage
- Compression latency

Available via Prometheus metrics:
- `litellm_compression_requests_total`
- `litellm_compression_savings_percent`
- `litellm_compression_latency_seconds`

### 3. Routing Strategy

**R1 Configuration (Current):**

LiteLLM uses simple round-robin routing with **NO automatic provider failover** to comply with R1 constraints.

```yaml
router_settings:
  routing_strategy: simple-shuffle  # Round-robin across available providers
  num_retries: 3  # Retry on same model/provider only
  timeout: 120
  # NO fallbacks configured - R1 constraint
```

**Why No Automatic Failover in R1?**

Per R1 architecture requirements, automatic provider failover is disabled to:
- Maintain predictable cost control
- Ensure explicit model selection by applications
- Simplify debugging and observability
- Allow manual intervention on provider failures

**R2+ Feature (Not Available in R1):**

Cost-based routing and automatic failover will be enabled in R2. This is currently disabled per R1 architecture requirements.

```yaml
# R2+ Configuration (Not supported in R1):
# router_settings:
#   routing_strategy: cost-based-routing
#   fallbacks:
#     - gpt-4o: ["claude-sonnet-4-5", "gemini-2-5-pro"]
#     - claude-sonnet-4-5: ["gpt-4o", "gemini-2-5-pro"]
```

### 4. Virtual Keys (Multi-Tenancy)

**Database-backed virtual keys** for multi-tenant isolation without per-tenant database overhead:

**Generate per-tenant API keys:**

```bash
curl http://localhost:4000/key/generate \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-001",
    "team_id": "tenant-001",
    "max_budget": 100.0,
    "models": ["gpt-4o-mini", "claude-haiku-3-5"],
    "duration": "30d",
    "rpm": 1000,
    "tpm": 100000,
    "aliases": {"gpt-4o-mini": "fast-model"}
  }'

# Response:
# {
#   "key": "sk-...",
#   "expires": "2025-11-28T00:00:00Z",
#   "user_id": "user-001",
#   "team_id": "tenant-001",
#   "max_budget": 100.0
# }
```

**Use virtual key for requests:**

```bash
# Use the generated virtual key (not master key)
curl http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-..." \
  -H "Content-Type: application/json" \
  -d '{
    "model": "fast-model",  # Uses alias
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

**Key Features:**
- **Budget enforcement** - Requests blocked when max_budget exceeded
- **Rate limiting** - Per-key RPM (requests per minute) and TPM (tokens per minute)
- **Model access control** - Restrict which models can be used
- **Model aliases** - Simplify model names for clients
- **Usage tracking** - All spend logged to PostgreSQL
- **Expiration** - Keys auto-expire after duration

**Check key usage:**

```bash
curl http://localhost:4000/key/info \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"key": "sk-..."}'

# Response:
# {
#   "key": "sk-...",
#   "user_id": "user-001",
#   "team_id": "tenant-001",
#   "spend": 2.45,
#   "max_budget": 100.0,
#   "budget_remaining": 97.55,
#   "models": ["gpt-4o-mini", "claude-haiku-3-5"],
#   "expires": "2025-11-28T00:00:00Z"
# }
```

**Delete key:**

```bash
curl -X POST http://localhost:4000/key/delete \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"key": "sk-..."}'
```

**R1 Multi-Tenancy Strategy:**
- Each tenant gets a virtual key with their own provider credentials (BYO LLM)
- Budget limits per tenant enforced at LiteLLM level
- Usage tracked in PostgreSQL for billing/reporting
- Semantic cache is namespace-isolated per tenant
- Platform API creates/manages virtual keys on tenant onboarding

## Monitoring

### Prometheus Metrics

Exposed at `http://localhost:4000/metrics`:

```
# Cache metrics
litellm_cache_hit_total
litellm_cache_miss_total

# Compression metrics
litellm_compression_requests_total
litellm_compression_savings_percent

# Request metrics
litellm_requests_total
litellm_request_duration_seconds
litellm_tokens_total
```

### Langfuse Integration

Automatic trace logging to Langfuse for:
- Request/response tracking
- Token usage
- Cost calculation
- Performance analysis

## Configuration

### Model Configuration

Edit `config/litellm_config.yaml` to add/remove models:

```yaml
model_list:
  - model_name: your-model-name
    litellm_params:
      model: provider/model-id
      api_key: os.environ/YOUR_API_KEY
      rpm: 10000
      tpm: 2000000
```

### Compression Settings

Edit `middleware/prompt_compression.py`:

```python
self.compression_config = {
    "default": {
        "enabled": True,
        "target_ratio": 0.5,  # Adjust compression ratio
        "min_tokens": 500      # Adjust minimum threshold
    }
}
```

## Troubleshooting

### Common Issues

**Issue: "No connection available" error**

Solution: Increase Redis max_connections in config:
```yaml
cache_params:
  max_connections: 200
```

**Issue: Compression fails silently**

Check logs for LLMLingua initialization errors:
```bash
docker-compose logs litellm-proxy | grep "LLMLingua"
```

**Issue: High latency**

Check compression overhead:
```bash
curl http://localhost:4000/metrics | grep compression_latency
```

## Development

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python -m litellm --config config/litellm_config.yaml --port 4000
```

### Adding Custom Middleware

1. Create new file in `middleware/`
2. Extend `CustomLogger` class
3. Register in `config/litellm_config.yaml`:

```yaml
litellm_settings:
  callbacks: ["your_custom_middleware"]
```

## Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Cache hit latency | <50ms | ✅ |
| Compression overhead | <50ms | ✅ |
| Compression ratio | 2-3x | ✅ |
| Cache hit rate | 40-60% | 🎯 |
| Total cost reduction | 70%+ | 🎯 |

## Related Documentation

- [Platform Architecture](../docs/project-docs/releases/R1/ARCHITECTURE.md)
- [Hybrid Gateway Migration](../docs/challenges/hybrid-architecture-migration.md)
- [LiteLLM Official Docs](https://docs.litellm.ai/)
- [LLMLingua Paper](https://arxiv.org/abs/2310.05736)

## Support

For issues specific to LiteLLM proxy:
1. Check logs: `docker-compose logs litellm-proxy`
2. Review configuration: `config/litellm_config.yaml`
3. Check metrics: `http://localhost:4000/metrics`
4. Refer to main platform documentation

## License

Part of D.Coder LLM Platform - 100% Open Source

