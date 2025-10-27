# Agents — LiteLLM Proxy (R1)

_Status: R1 LLM gateway workstream — caching, compression, and quota events._

## Scope & Mission
- Configure LiteLLM to route OpenAI, Anthropic, Google, and Groq models with Redis semantic caching and prompt compression.
- Manage virtual keys, enforce per-tenant budgets, and emit `quota.updated` events for Platform API reconciliation.

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
- [Architecture](../../docs/project-docs/releases/R1/ARCHITECTURE.md)
- [Service Contracts](../../docs/project-docs/releases/R1/SERVICE_CONTRACTS.md)

## R1 Conventions
- Guardrails detect-only; quotas enforced via LiteLLM and mirrored to Platform API.
- Maintain required headers and shared error envelope for exposed endpoints.
- Metrics must cover cache hits/misses, compression savings, cost tracking.

## Task & Commit Protocol
- Complete roadmap items sequentially, ensuring tests and configs for each step are updated. Pause only for user-provided answers.
- Commit using Conventional Commits and push; configure git user (Manan Ramnani) if needed.

## Context & Research Workflow
- Review docs and current config prior to changes.
- Use **Context7 MCP** for LiteLLM, Redis, LLMLingua, or provider SDK documentation.
- Use **Exa MCP (web_search)** for cost-routing patterns or middleware guidance.
- Use **Perplexity MCP** for supplementary info; prioritize official docs when conflicts arise.
- Record research notes before implementation.
- Strictly adhere to referenced documentation; if uncertainty remains, pause and ask the user before proceeding.

## Service Boundaries & Dependencies
- Work within `services/litellm-proxy/**` unless coordinating tasks explicitly require cross-service edits.
- Integrate with Redis (cache), PostgreSQL (virtual keys), Kong (routing separation), Platform API (quota sync).
- Ensure outbound calls respect provider allowlists defined in infrastructure policies.

## Testing & Verification
- Run unit tests for middleware, caching, and key management.
- Execute integration tests against mock providers or sandboxes; confirm cache hit/miss and compression metrics.
- Verify `/health` and `/metrics` endpoints remain healthy.

## Roadmap Tracking
- Update progress indicators inside [09-Roadmap](./docs/09-Roadmap.md); maintain one active `in_progress` item at a time.

## Clarifications & Collaboration
- Ask the user for clarification when provider behavior, quotas, or compression policies are uncertain.

## Security & Compliance
- Never check secrets into source; rely on environment variables and secure storage.
- Enforce virtual key scopes, log redaction, and respect tenant isolation.

## Tooling Notes
- Use docker-compose to run Redis/PostgreSQL dependencies.
- Monitor Prometheus metrics and Langfuse traces whenever features are added.
