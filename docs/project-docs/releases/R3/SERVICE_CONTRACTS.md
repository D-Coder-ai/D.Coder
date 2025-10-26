# R3 Service Contracts

## Policies
- Guardrails
  - PUT `/v1/policies/guardrails/mode` { mode: "block" }
  - POST `/v1/policies/overrides` { scope, reason, expiresAt }

## Tenancy
- Residency
  - GET/PUT `/v1/tenants/{tenantId}/residency` { region }
- Offboarding
  - POST `/v1/tenants/{tenantId}/offboard` (async)
  - Events: `tenant.offboarding.started|completed`

## AI Gateway Admin
- Cache namespaces: tenant+provider+model
- POST `/v1/cache/invalidate` { namespace, ttlOverride? }

## Events
- `guardrail.blocked`, `policy.override.created`

## Compatibility
- APIs remain v1; additive endpoints only
