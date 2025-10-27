 # Integrations
 
 Consumes
 - Platform API: tenant context, provider configs, quotas
 - Knowledge & RAG: `/v1/rag/search` for retrieval
 - LiteLLM Proxy: OpenAI-compatible chat/completions
 - Integrations: webhook callbacks and async signals
 
 Exposes
 - Orchestration APIs under `/v1/workflows/*` via Kong routes
 - Emits `workflow.*` events for observability and triggers
 
 Call rules
 - All outbound HTTP calls go via Kong Gateway except direct LiteLLM (port 4000)
 - Include global headers on every call; propagate `X-Request-Id` and `X-Trace-Id`
 
 References: [Architecture](../../../docs/project-docs/releases/R1/ARCHITECTURE.md) • [Service Contracts](../../../docs/project-docs/releases/R1/SERVICE_CONTRACTS.md)
