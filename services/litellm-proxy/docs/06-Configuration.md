# Configuration

Files
- `config/litellm_config.yaml` (models, routing, cache)

Env vars

## Required
- Provider keys (OpenAI, Anthropic, Google, Groq)
  - `OPENAI_API_KEY`
  - `ANTHROPIC_API_KEY`
  - `GOOGLE_API_KEY`
  - `GROQ_API_KEY`
- `REDIS_URL` - Redis connection string for caching
- `DATABASE_URL` - PostgreSQL connection string for virtual keys
- `LITELLM_MASTER_KEY` - Master key for admin operations

## Optional - Compression Settings
Prompt compression is configurable per profile (default, RAG, chat) via environment variables:

**Default Profile:**
- `COMPRESSION_DEFAULT_RATIO` - Compression ratio (default: `0.5` for 2x compression)
- `COMPRESSION_DEFAULT_MIN_TOKENS` - Minimum tokens to trigger compression (default: `500`)

**RAG Profile** (triggered by `x-rag: true` header):
- `COMPRESSION_RAG_RATIO` - Compression ratio (default: `0.33` for 3x compression)
- `COMPRESSION_RAG_MIN_TOKENS` - Minimum tokens to trigger compression (default: `1000`)

**Chat Profile** (triggered by `x-chat: true` header):
- `COMPRESSION_CHAT_RATIO` - Compression ratio (default: `0.6` for 1.67x compression)
- `COMPRESSION_CHAT_MIN_TOKENS` - Minimum tokens to trigger compression (default: `300`)

Compression profiles are selected automatically based on request metadata headers:
- Send `x-rag: true` in request metadata for RAG-optimized compression
- Send `x-chat: true` in request metadata for chat-optimized compression
- No header defaults to standard compression profile

## Optional - Event Publishing
- `NATS_URL` - NATS server URL for quota event publishing (defaults to stdout if not set)
- `NATS_QUOTA_SUBJECT` - NATS subject for quota events (default: `quota.updated`)
- `NATS_CONNECT_TIMEOUT` - NATS connection timeout in seconds (default: `2.0`)

References: [Service README](../README.md) • [Configuration Model](../../../docs/project-docs/releases/R1/CONFIGURATION.md)
