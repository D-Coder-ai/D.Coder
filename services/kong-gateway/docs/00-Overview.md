 # Kong Gateway — R1 Overview
 
 Purpose: Platform API routing, request/response transforms, per-tenant rate limiting, observability; hybrid gateway with LiteLLM Proxy.
 
 In scope (R1)
 - Declarative config for services/routes/plugins
 - Rate limiting with Redis
 - Correlation IDs, Prometheus metrics
 - Mirrors quotas from LiteLLM via Platform API
 
 Out of scope (R1)
 - Automatic provider failover; complex WAF policies
 
 Quickstart
 - Ports: 8000 (proxy), 8001 (admin)
 - Health: GET /status (admin)
 - Config: `services/kong-gateway/config/kong.yml`
 
 References: [Service README](../README.md) • [Architecture](../../../docs/project-docs/releases/R1/ARCHITECTURE.md) • [Service Contracts](../../../docs/project-docs/releases/R1/SERVICE_CONTRACTS.md)
