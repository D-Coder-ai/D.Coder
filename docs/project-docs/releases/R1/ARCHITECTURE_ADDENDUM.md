# Release R1 (Beta / MVP) — Architecture Addendum

This addendum constrains and clarifies the platform architecture for R1.

## Scope Decisions
- Hosting: Dual‑mode (env‑driven) deployments.
- BYO LLM per tenant; local/on‑prem inference not required in R1.
- Data egress: allowlisted public LLM endpoints.
- Tenant isolation: Database per tenant.
- Quotas/budgets: enforce at Kong and mirror in Platform API.
- Guardrails: alert‑only (no hard block) for prompt‑injection/DLP.
- Providers supported: OpenAI, Anthropic, Google, Groq.
- SSO: Logto. Feature flags: Flagsmith.
- Backups/DR: daily encrypted backups; RPO 24h, RTO 4h.
- No automatic provider failover in R1 (manual switch only).

## Plugin Architecture (Integrations)
- Connectors (Jira, Slack, Teams, SharePoint, Confluence, Linear, Bitbucket) are optional plugins.
- Plugins are configured at platform level and enabled per tenant via Flagsmith.
- Standardized plugin interface: lifecycle (install, enable, configure, disable); secrets isolated per tenant.

## Configuration Model
- Platform configuration defines defaults for any platform derived from D.Coder.
- Tenant configuration overrides: LLM providers/keys, quotas, feature flags, enabled integrations, UI branding.

## Deferred Items
- Prompt IP encryption with per‑tenant keys (R2).
- Conversation archival/retention (R2).
- Data residency/air‑gap posture (R3).
- Offboarding/kill switch runbook (R3).
- Semantic cache isolation policy (R3).

## Documentation Cross‑References
- R1 PRD: ./PRD.md
- Configuration Model: ./CONFIGURATION.md
- Plugin Architecture: ./PLUGIN_ARCHITECTURE.md
- Agent Engineering Brief: ./AGENT_ENGINEERING_BRIEF.md
- Service Contracts: ./SERVICE_CONTRACTS.md


