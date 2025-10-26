# R4 Service Contracts (GA)

## Ops
- SLOs
  - GET `/v1/ops/slos`
  - PUT `/v1/ops/slos` (admin)
- DR
  - POST `/v1/ops/dr/tests` (schedule)

## Marketplace
- Plugins catalog with versions and constraints
  - GET `/v1/plugins`
  - POST `/v1/plugins/{plugin}/install`
  - POST `/v1/plugins/{plugin}/rollback`

## Providers
- Optional auto failover policy
  - PUT `/v1/tenants/{tenantId}/providers/policies` { failover: { enabled, maxSpend, allowedProviders } }
  - Events: `provider.failover.triggered|completed`

## Compatibility
- Maintain v1; document deprecation schedule for older fields
