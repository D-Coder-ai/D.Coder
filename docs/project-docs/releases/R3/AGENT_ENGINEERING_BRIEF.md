# R3 Agent Engineering Brief

## Goals
- Enforce guardrails; add residency/egress; implement offboarding; isolate semantic cache

## Constraints
- Policies block with auditable overrides; tenant-level configurations
- Residency region determines data stores and egress allowlists

## New Endpoints/Events
- Offboarding: `POST /v1/tenants/{tenantId}/offboard` (async)
- Guardrail overrides: `POST /v1/policies/overrides`
- Cache: admin endpoints for invalidation by namespace

## Config
- `residency.region`, `egress.allowlist`
- Cache: `semanticCache.ttl`, `namespace`

## Handoff
- See `./ARCHITECTURE.md`, `./SERVICE_CONTRACTS.md`, `./DATA_RESIDENCY_AND_EGRESS.md`
