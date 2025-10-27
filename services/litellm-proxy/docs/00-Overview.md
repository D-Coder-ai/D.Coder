 # LiteLLM Proxy — R1 Overview
 
 Purpose: Specialized LLM gateway with multi-provider routing, Redis-backed semantic caching, optional prompt compression, and cost tracking.
 
 In scope (R1)
 - OpenAI-compatible API at port 4000
 - Redis-backed semantic caching
 - Prompt compression middleware (LLMLingua)
 - Virtual keys for multi-tenancy; cost/budget tracking
 - Emit `quota.updated` events for Platform API reconciliation
 
 Out of scope (R1)
 - Automatic provider failover
 
 Quickstart
 - Port: 4000; Health: GET /health; Metrics: /metrics
 - Config: `config/litellm_config.yaml`
 
 References: [Service README](../README.md) • [Architecture](../../../docs/project-docs/releases/R1/ARCHITECTURE.md) • [Service Contracts](../../../docs/project-docs/releases/R1/SERVICE_CONTRACTS.md)
