# @dcoder/litellm-proxy

## 1.0.0

### Major Changes

- Initial release of LiteLLM Proxy service for R1
- Multi-provider LLM routing (OpenAI, Anthropic, Google, Groq)
- Redis semantic caching with 0.8 similarity threshold (40-60% token reduction)
- Virtual keys for multi-tenant API key management
- LLMLingua prompt compression middleware (20-30% token reduction)
- Simple-shuffle routing (cost-based routing and automatic failover deferred to R2 per R1 constraints)
- Langfuse and Prometheus observability integration
- Docker Compose integration (base infrastructure + standalone dev)

### R1 Constraints Compliance

- ✅ NO automatic provider failover (manual switch only)
- ✅ BYO LLM credentials per tenant via virtual keys
- ✅ Alert-only guardrails (no hard blocking)
- ✅ Database-per-tenant isolation via virtual keys

### Configuration

- Port 4000 exposed for LLM traffic
- PostgreSQL database for virtual key persistence
- Redis for semantic caching and rate limiting
- Health checks and dependency management

