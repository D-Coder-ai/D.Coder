# Agents — Platform API (R1)

_Status: R1 core governance workstream — tenancy, auth, quotas, providers._

## Scope & Mission
- Implement multi-tenant Platform API (FastAPI) covering Tenants, Users, Quotas, Providers, Auth (Logto), ABAC (Casbin), and Flagsmith-driven feature flags.
- Reconcile usage with LiteLLM `quota.updated` events and expose governance APIs consumed by other services.

## References
- [00-Overview](./docs/00-Overview.md)
- [01-Requirements](./docs/01-Requirements.md)
- [02-Architecture](./docs/02-Architecture.md)
- [03-APIs](./docs/03-APIs.md)
- [04-Events](./docs/04-Events.md)
- [05-Integrations](./docs/05-Integrations.md)
- [06-Configuration](./docs/06-Configuration.md)
- [07-Security-and-Guardrails](./docs/07-Security-and-Guardrails.md)
- [08-Testing-and-Observability](./docs/08-Testing-and-Observability.md)
- [09-Roadmap](./docs/09-Roadmap.md)
- [10-Glossary](./docs/10-Glossary.md)
- [Service README](./README.md)
- [Platform PRD](../../docs/project-docs/releases/R1/PRD.md)
- [Architecture](../../docs/project-docs/releases/R1/ARCHITECTURE.md)
- [Service Contracts](../../docs/project-docs/releases/R1/SERVICE_CONTRACTS.md)

## R1 Conventions
- Enforce global headers and error envelopes; guardrails detect-only.
- Quotas double-entry: at Kong/LiteLLM plus Platform API reconciliation.
- Tenant isolation via DB-per-tenant; audit everything.

## Task & Commit Protocol
- Complete each roadmap item (including migrations, tests, docs updates) before starting the next; pause only for user responses.
- Finish with Conventional Commit and push; configure git user (Manan Ramnani) if needed.

## Context & Research Workflow
- Review service docs, current domain models, migrations before changes.
- Use **Context7 MCP** for FastAPI, Pydantic, Alembic, Casbin, Logto, Flagsmith official docs.
- Use **Exa MCP (web_search)** to explore patterns/best practices when necessary.
- Use **Perplexity MCP** for supplementary context; follow official docs when conflicting.
- Record research findings before coding.
- Strictly follow the referenced documentation; consult the user immediately when conflicts or gaps appear.

## Service Boundaries & Dependencies
- Edit within `services/platform-api/**` unless the task explicitly touches other services.
- Coordinate with LiteLLM events, Flagsmith configuration, Redis cache, and database provisioning.
- All outbound requests (if any) must flow through Kong.

## Testing & Verification
- Maintain unit tests for domain and application layers, integration tests for adapters, and E2E tests for key workflows.
- Run migrations (Alembic) and ensure `/health*`, `/metrics`, and auth flows operate correctly.

## Roadmap Tracking
- Update [09-Roadmap](./docs/09-Roadmap.md) statuses as you progress; keep only one `in_progress` item at a time and mark completions immediately.

## Clarifications & Collaboration
- Ask the user whenever requirements, quotas, or auth scenarios are ambiguous. Do not assume defaults.

## Security & Compliance
- Protect secrets (no hardcoding); enforce ABAC and audit logging.
- Ensure data encryption hooks are in place where specified; guardrails remain detect-only but must log findings.

## Tooling Notes
- Use docker-compose databases (admin + tenant) and Redis during development.
- Validate reconciliation loops with LiteLLM event streams before shipping.
