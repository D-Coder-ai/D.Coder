# R1 Service Contracts (APIs, Events, Conventions)

Status: Planning contracts for consistent implementation in R1

## Global API Conventions
- Base: `/v1`
- Media: `application/json`
- Headers (all services): `X-Request-Id`, `X-Tenant-Id`, `X-Platform-Id`, `X-User-Id`, `X-Trace-Id`, optional `Idempotency-Key`
- Pagination: `?limit=&cursor=`; responses include `items`, `nextCursor`
- Errors: `{ "error": { "code": "string", "message": "string", "details": {...} } }`

## Event Conventions (NATS JetStream)
- Subject: `domain.action`
- Envelope: `{ eventId, occurredAt, tenantId, platformId, correlationId, actor, payload }`

## AI Gateway (Hybrid: Kong Gateway + LiteLLM)
- Responsibilities split:
  - Kong Gateway: platform API routing, request transformation, rate limits, quota mirroring events (`quota.updated`).
  - LiteLLM Proxy: LLM routing, Redis-backed semantic cache, optional prompt compression middleware, cost tracking, emits `quota.updated` events for Platform API reconciliation.
- Route naming: `llm.{provider}.{model}`