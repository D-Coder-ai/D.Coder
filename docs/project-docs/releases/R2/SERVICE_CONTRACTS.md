# R2 Service Contracts

## Global
- Headers: X-Request-Id, X-Tenant-Id, X-Platform-Id, X-User-Id, X-Trace-Id, Idempotency-Key
- Errors: { error: { code, message, details } }
- Events: subject `domain.action`, include tenantId, correlationId

## Platform API
- Providers
  - PUT `/v1/tenants/{tenantId}/providers` (accepts `secretRef` fields)
- Archival
  - POST `/v1/archive/export` { range, filters }
  - GET `/v1/archive/retention` / PUT to update `{ retentionDays }`
- Usage/Quotas
  - GET `/v1/tenants/{tenantId}/usage?from=&to=`

## Agent Orchestrator
- Events: `conversation.archived` { conversationId, tenantId, retention, checksum }

## AI Gateway
- No automatic provider failover; quotas enforced; detect-only guardrails

## Knowledge & RAG
- Unchanged from R1

## Forward-compat (R3 hooks)
- Guardrail policy mode `detect|block` (R2 fixed to `detect`)
- Residency region field on tenant config (inactive in R2)
