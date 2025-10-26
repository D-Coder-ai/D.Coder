# Release R1 (Beta / MVP) — Product Requirements Document (PRD)

Platform: D.Coder

Initial Tenant: Deloitte USI IGS

Status: Planning — Documentation-First (no development scope in this release cycle document)

## 1. Goals
- Deliver a working MVP proving core value: multi-LLM routing, prompt iteration, RAG, and basic admin/observability.
- Require BYO LLM credentials per tenant; no local/on‑prem inference.
- Keep security/compliance light in R1 but architect for future scale (R2–R4).
- Establish plugin-first approach for integrations (Jira/Slack/Teams/SharePoint/etc.).

## 2. Non‑Goals
- Conversation archival and legal holds (planned R2).
- Prompt IP encryption with per-tenant KEKs (planned R2).
- Data residency/air‑gap posture and offboarding runbook (planned R3).
- Automatic model/provider failover (not in R1).

## 3. In‑Scope (Functional)
- AI Gateway: Hybrid gateway (Kong Gateway + LiteLLM proxy) for LLM routing.
  - LiteLLM handles Redis-backed semantic caching and optional prompt compression middleware.
  - Providers: OpenAI, Anthropic, Google, Groq.
  - BYO credentials per tenant; egress allowlist for public LLM endpoints.
  - Guardrails: alert‑only (no hard blocking in R1); no automatic provider failover.
- LLMOps: Agenta; MLFlow; Langfuse.
- Platform API: Multi‑tenancy, ABAC, quotas, usage tracking, feature flags.
- Knowledge & RAG: pgvector MVP; LlamaIndex orchestration.
- Integrations: Plugin scaffold only; no mandatory connector in R1.
- Clients: Open WebUI for Doc Chat and Code Chat; Admin dashboard MVP; Deloitte dashboard MVP.

## 4. In‑Scope (Non‑Functional)
- Tenant isolation: Database per tenant.
- Quotas and budgets: Enforce at Kong and mirrored in Platform API.
- Backups/DR: Daily encrypted backups; RPO 24h, RTO 4h.
- Observability: Prometheus, Grafana, Loki, OpenTelemetry, Langfuse.
- SSO/IdP: Logto (R1 default).
- Feature flags: Flagsmith.

## 5. Out of Scope (R1)
- Local/on‑prem inference (vLLM/Ollama).
- Per‑tenant KEK/DEK envelope encryption for prompts (Vault) — R2.
- Conversation archival and export — R2.
- Data residency policies/air‑gap — R3.
- Offboarding/kill switch runbook — R3.
- Semantic cache isolation/invalidation policy — R3.

## 6. Product Requirements
- Authentication/Authorization
  - Use Logto with OIDC; roles mapped via ABAC (Casbin).
  - Tenant onboarding flow creates dedicated database and default roles.
- LLM Routing
  - Define per‑tenant provider configurations and API keys.
  - No automatic failover; manual switch only.
  - Egress allowlist enforced for LLM endpoints.
- Quotas & Usage
  - Rate limits at gateway (per tenant) with mirrored enforcement in Platform API.
  - Tenant‑level budgets for LLM spend; soft alerts only in R1.
- Feature Flagging (Flagsmith)
  - Flags control: integrations/plugins, experimental features, per‑tenant rollouts.
  - Implement global/platform and per‑tenant segments.
- RAG
  - pgvector for embeddings; hybrid retrieval (BM25+dense) default.
  - Document parsing via Unstructured; ingestion jobs tracked.
- Clients
  - Open WebUI: two instances (Doc Chat, Code Chat) with per‑tenant configuration.
  - Admin/Deloitte dashboards: KPIs include cost ceilings, burn‑down, success/error, latency P95, cache hit rate.
- Integrations
  - Plugin architecture available; connectors ship disabled by default.

## 7. Configuration Model
- Platform‑level configuration (applies to all platforms based on D.Coder) separate from tenant‑level.
- Tenant‑level overrides for LLM providers/keys, quotas, features, and integrations.
- See: ../configuration/PLATFORM_AND_TENANT_CONFIGURATION.md

## 8. Acceptance Criteria
- Multi‑tenant sign‑in via Logto; creation of a new tenant provisions its own database.
- Per‑tenant LLM calls succeed with BYO credentials; egress allowlist enforced.
- Quotas enforced at gateway with mirrored counters in Platform API.
- RAG queries return grounded answers for loaded sample corpus.
- Dashboards display KPIs listed above; feature flags can toggle integrations.
- Documentation published for R1 PRD and Architecture Addendum; links referenced from main architecture.

## 9. Risks & Mitigations
- Over‑engineering security in R1 → Mitigate by deferring to R2/R3 but designing extensible seams (plugins, configs).
- Quota drift between gateway and API → Mitigate with mirrored counters and reconciliation jobs.
- Provider policy changes → Mitigate via plugin/provider abstraction and Flagsmith toggles.

## 10. Release Criteria
- All acceptance criteria satisfied in a controlled environment with demo data.
- Documentation sign‑off: PRD, architecture addendum, configuration model, plugin architecture.


