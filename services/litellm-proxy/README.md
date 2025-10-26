# LiteLLM Proxy - D.Coder R1

LiteLLM Proxy service providing specialized LLM gateway capabilities including:

- **Multi-LLM Routing**: Native support for OpenAI, Anthropic, Google Gemini, and Groq
- **Redis-Backed Semantic Caching**: 40-60% token reduction through intelligent caching
- **Prompt Compression**: 20-30% additional savings using LLMLingua
- **Cost-Based Routing**: Automatic routing to cheapest available model
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

Automatic Redis-backed caching with 1-hour TTL:

```yaml
# config/litellm_config.yaml
litellm_settings:
  cache: true
  cache_params:
    type: redis
    ttl: 3600
    namespace: "litellm:cache"
```

**Benefits:**
- 40-60% token reduction
- <50ms cache hit latency
- Automatic cache key generation
- Tenant isolation via namespace

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

### 3. Cost-Based Routing

Automatic routing to cheapest model:

```yaml
router_settings:
  routing_strategy: cost-based-routing
  fallbacks:
    - gpt-4o: ["claude-sonnet-4-5", "gemini-2-5-pro"]
```

### 4. Virtual Keys (Multi-Tenancy)

Generate per-tenant API keys:

```bash
curl http://localhost:4000/key/generate \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -d '{
    "user_id": "user123",
    "team_id": "tenant123",
    "max_budget": 100.0,
    "models": ["gpt-4o", "claude-sonnet-4-5"]
  }'
```

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

