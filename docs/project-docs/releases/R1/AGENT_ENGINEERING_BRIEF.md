# R1 Agent Engineering Brief (for AI Coding Agents)

Platform: D.Coder (reusable foundation)
Initial Tenant: Deloitte USI IGS
Scope: Documentation-first; build planning and contracts only for R1

## 1) R1 Snapshot (What to optimize for)
- Goals: Core functionality; fast delivery; cohesive cross-service integration.
- Hosting: Dual-mode (env-driven).
- LLM: BYO per tenant; providers: OpenAI, Anthropic, Google/Vertex, Groq.
- No local/on‑prem inference in R1.
- Guardrails: alert-only (no blocking).
- Quotas: enforce at Kong + mirror in Platform API.
- Isolation: Database per tenant.
- SSO: Logto. Feature flags: Flagsmith.
- Backups/DR: daily encrypted backups; RPO 24h, RTO 4h.
- No automatic provider failover.

References: `docs/project-docs/releases/R1/PRD.md`, `docs/project-docs/releases/R1/ARCHITECTURE_ADDENDUM.md`, `docs/PLATFORM_ARCHITECTURE.md`

## 2) Services and Responsibilities (R1)
- AI Gateway (Kong): LLM routing, semantic cache, prompt compression, rate limits, alert-only guardrails.
- Platform API: tenancy, ABAC, quotas/usage, feature flags, provider configs.
- Agent Orchestrator: workflow entrypoints, tool routing, NATS subjects.
- Knowledge & RAG: ingestion, indexing (pgvector), search API.
- Integrations: plugin catalog scaffolding; per-tenant enable/disable; no mandatory connectors.
- Clients: Open WebUI (Doc Chat, Code Chat), Admin dashboard MVP, Deloitte dashboard MVP.

References: `docs/project-docs/releases/R1/SERVICE_CONTRACTS.md`

## 3) Configuration Model (what to pass to agents)
- Platform-level config: platform name/branding, default providers, global flags.
- Tenant-level config (override defaults):
  - Identity: tenantId, tenantName, platformId.
  - SSO (Logto): issuerUrl, clientId, clientSecret, redirectUris.
  - Flagsmith: apiKey, environment, segment keys.
  - LLM providers: openai.apiKey, anthropic.apiKey, google.vertex.* creds, groq.apiKey.
  - Quotas/budgets: per-tenant rate limits, monthly token/spend ceilings (alert-only in R1).
  - Egress allowlist: allowed LLM endpoints/domains.
  - RAG defaults: embedding model, chunk sizes, hybrid retrieval on/off.
  - UI: branding overrides; enabled plugins list.

Reference: `docs/project-docs/releases/configuration/PLATFORM_AND_TENANT_CONFIGURATION.md`

## 4) Cross-service Conventions (must be consistent)
- Headers: `X-Request-Id`, `X-Tenant-Id`, `X-Platform-Id`, `X-User-Id`, `X-Trace-Id`.
- API: JSON; versioning `/v1`; pagination (limit, cursor); idempotency via `Idempotency-Key`.
- Errors: envelope `{ error: { code, message, details } }` with stable codes.
- Observability: OTel traces; logs redacted; labels include tenantId, platformId, service, route.
- Events: NATS JetStream subjects `domain.action` with `tenantId`, `correlationId`.

## 5) R2 Forward-Compatibility Seams (design now, implement later)
- Prompt IP encryption (R2): store secrets as references; abstraction for key management; in-memory decryption seam.
- Conversation archival (R2): emit standardized audit events; durable storage interface; retention policy hook.
- Guardrail enforcement (R3): policy engine interface (detect-only → block modes); override mechanism.
- Residency/egress (R3): region attribute on tenant; egress policy hook.
- Offboarding (R3): orchestrated deprovision sequence; cache flush hooks; job pause hooks.
- Semantic cache isolation (R3): cache key namespace: tenant+provider+model; TTL support.

References: `docs/project-docs/releases/security/PROMPT_ENCRYPTION.md`, `docs/project-docs/releases/security/GUARDRAILS_AND_DLP.md`

## 6) Definition of Done (R1 Planning)
- PRDs and Architecture Addenda cross-linked; service contracts drafted; configuration keys defined.
- APIs and events designed with versioning and error model.
- KPI definitions finalized for dashboards (cost ceilings, burn-down, success/error, latency P95, cache hit rate).

## 7) Handoff Package (give AI agents these files)
- Original Ask: `docs/project-docs/plans/original-ask.md`
- Releases overview: `docs/project-docs/releases/RELEASES_OVERVIEW.md`
- R1 PRD + Addendum: `docs/project-docs/releases/R1/PRD.md`, `docs/project-docs/releases/R1/ARCHITECTURE_ADDENDUM.md`
- Service contracts: `docs/project-docs/releases/R1/SERVICE_CONTRACTS.md`
- Plugin architecture: `docs/project-docs/releases/plugins/PLUGIN_ARCHITECTURE.md`
- Config model: `docs/project-docs/releases/configuration/PLATFORM_AND_TENANT_CONFIGURATION.md`
- Guardrails (R1 detect-only): `docs/project-docs/releases/security/GUARDRAILS_AND_DLP.md`
- Prompt encryption (R2 plan): `docs/project-docs/releases/security/PROMPT_ENCRYPTION.md`

## 8) Seed Values (R1)
- Platform: name = "D.Coder".
- Tenant: name = "Deloitte USI IGS"; isolation = DB-per-tenant.
- Providers enabled: OpenAI, Anthropic, Google/Vertex, Groq (BYO keys).
- SSO: Logto; Feature flags: Flagsmith.
