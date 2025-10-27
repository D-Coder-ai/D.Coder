# Agents — Integrations (R1)

_Status: R1 plugin scaffold work in progress — focus on connectors and webhooks._

## Scope & Mission
- Provide tenant-scoped plugin infrastructure for Jira, Bitbucket, Confluence, SharePoint connectors.
- Handle webhook ingestion, HMAC validation, async jobs, and `integration.*` events for downstream consumers and MCP tools.

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
- [Plugin Architecture](../../docs/project-docs/releases/R1/PLUGIN_ARCHITECTURE.md)
- [Platform PRD](../../docs/project-docs/releases/R1/PRD.md)

## R1 Conventions
- Guardrails detect-only; enforce required headers and error envelopes.
- Events must use shared envelope; subjects under `integration.*`.
- Respect per-tenant enable/disable via Flagsmith.

## Task & Commit Protocol
- Finish all subtasks for a roadmap item before moving on. Pause only for pending user answers.
- After completion: `git add`, Conventional Commit, push. Configure git user (Manan Ramnani) if absent.

## Context & Research Workflow
- Gather necessary context from docs and existing code first.
- Use **Context7 MCP** for official SDK/API docs (Jira, Bitbucket, Microsoft Graph, etc.).
- Use **Exa MCP (web_search)** for integration patterns or webhook best practices.
- Use **Perplexity MCP** for general background; prefer official docs when discrepancies occur.
- Record research notes before implementation.
- Strictly follow the referenced documentation; if requirements or docs conflict, pause and ask the user.

## Service Boundaries & Dependencies
- Modify files under `services/integrations/**` unless cross-service work is specified.
- Outbound HTTP calls to external SaaS may bypass Kong but must honor security policies; internal service calls route via Kong.
- Manage Celery/Redis workers, NATS JetStream publishing, MCP tool adapters here.

## Testing & Verification
- Provide unit tests for plugin registry, webhook validators, API adapters.
- Integration/E2E tests should cover plugin enablement, webhook reception, and event emission.
- Verify health endpoints remain operational.

## Roadmap Tracking
- Update status entries within [09-Roadmap](./docs/09-Roadmap.md). Keep only one item `in_progress`; mark completion immediately once done.

## Clarifications & Collaboration
- If requirements, connector behaviors, or permissions are unclear, ask the user—never assume defaults.

## Security & Compliance
- Store no credentials in repo; rely on tenant configuration and secure storage.
- Enforce HMAC/signature validation, rate limiting (via Kong), and log sanitization.
- Guardrails detect-only; log suspicious payloads for review.

## Tooling Notes
- Ensure Redis, NATS, and required external API sandboxes are configured.
- Follow Flagsmith segments for per-tenant plugin toggles.
