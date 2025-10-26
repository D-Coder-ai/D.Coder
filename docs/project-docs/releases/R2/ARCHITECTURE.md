# D.Coder — R2 Architecture Guide

Scope: Release Preview. Builds on R1, adds prompt encryption and conversation archival while keeping guardrails detect-only.

## Snapshot
- Hosting: Dual-mode
- LLM: BYO per tenant; providers: OpenAI, Anthropic, Google/Vertex, Groq
- Guardrails: detect-only (alerts)
- Quotas: enforce at Kong + mirror in Platform API
- Isolation: DB-per-tenant
- SSO: Logto; Flags: Flagsmith
- New: Prompt IP encryption (KEK/DEK); Conversation archival

## Services
- AI Gateway (Kong): routing, cache, compression, rate limits, detect-only guardrails
- Platform API: tenancy, ABAC, quotas/usage, flags, provider configs; archival controls
- Agent Orchestrator: workflows, events; emits archival events
- Knowledge & RAG: pgvector; LlamaIndex
- Integrations: plugin-first; per-tenant enablement
- Clients: Open WebUI x2; Admin + Deloitte dashboards

## Security & Compliance (R2)
- Prompt IP: see `./PROMPT_ENCRYPTION.md`
- Archival: tenant-configurable retention; encrypted at rest
- Guardrails: see `./GUARDRAILS_AND_DLP.md`

## Configuration
- See `./CONFIGURATION.md` (adds secretRef and retention settings)

## Plugins
- See `./PLUGIN_ARCHITECTURE.md`

## References
- PRD: `./PRD.md`
- Addendum: `./ARCHITECTURE_ADDENDUM.md`
- Agent brief: `./AGENT_ENGINEERING_BRIEF.md`
- Service contracts: `./SERVICE_CONTRACTS.md`
