# Platform and Tenant Configuration Model (R1)

## Goals
- Support multiple platform brands reusing core services (starting with D.Coder).
- Clean separation between platform defaults and tenant overrides.

## Configuration Layers

### Platform-Level (Authoritative Defaults)
- Branding (name, logos, color palette).
- Default LLM providers, routing policies, and per-provider allowlists.
- Global feature flags and plugin catalog scope.
- Central quotas / budgets mirrored to tenants.
- Observability endpoints and logging policy.

Configuration artifacts live in `infrastructure/policies/` (allowlisted provider hosts, OPA rules), `services/kong-gateway/config/` (declarative gateway config rendered into Docker compose), and `services/litellm-proxy/config/` (provider + virtual key policies).

### Tenant-Level (Overrides & Secrets)
- LLM providers/keys (stored as virtual keys in LiteLLM; BYO credentials enforced).
- Quotas/budgets, RAG corpus assignments, residency region (R3+).
- Enabled integrations/plugins via Flagsmith segments.
- UI branding overrides and custom dashboards.

Tenant configuration persists in each tenant database (DB-per-tenant) exposed via the Platform API. LiteLLM virtual keys reference tenant-scoped credentials with metadata kept in `services/litellm-proxy/config/`.

## Storage & Access
- Platform defaults: configuration service backed by PostgreSQL (shared schema) with JSON Schema validation. Cached in Redis for fast reads.
- Tenant config: stored within the tenant database; surfaced to services through Platform API read models.
- Flagsmith segments: map platform defaults to tenant overrides (reconcile nightly).

## Operational Flow
1. Platform admin updates defaults → persisted in configuration store → Kong Gateway declaratives regenerated via CI.
2. Tenant admin updates overrides via Platform API → stored in tenant DB → propagated to LiteLLM virtual keys and Flagsmith.
3. Infrastructure policies (e.g., `infrastructure/policies/allowed_provider_hosts.yaml`) version the global allowlist consumed by both Kong and LiteLLM.

## Roadmap
- R2: Introduce secure secret references (Vault/KMS) for sensitive fields; extend LiteLLM to pull secrets dynamically.
- R3: Add residency/egress policies and semantic cache isolation toggles per tenant.
- R4: Add configuration versioning, audit trails, and rollback workflow.
