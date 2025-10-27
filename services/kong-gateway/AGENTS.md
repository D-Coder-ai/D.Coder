# Agents — Kong Gateway (R1)

_Status: R1 declarative gateway configuration — ensure platform routing, rate limits, and observability._

## Scope & Mission
- Maintain Kong declarative configuration to route platform services, enforce quotas, and expose observability endpoints.
- Coordinate with LiteLLM proxy by keeping LLM routes separate while mirroring quota data.

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
- Required headers and error schema enforced via plugins or upstream policies.
- Guardrails detect-only; rate limiting relies on Redis-backed plugin.
- Prometheus, correlation-id, http-log plugins must remain active.

## Task & Commit Protocol
- Complete roadmap items sequentially; keep work scoped to Kong config and supporting scripts. Pause only for user clarifications.
- On completion: stage changes, apply Conventional Commit, push; set git user (Manan Ramnani) if needed.

## Context & Research Workflow
- Review declarative config and docs before editing.
- Use **Context7 MCP** for official Kong and plugin documentation.
- Use **Exa MCP (web_search)** for community examples or troubleshooting rate-limit/correlation patterns.
- Use **Perplexity MCP** for supplemental background; rely on official docs when conflicting.
- Capture research outputs before coding.
- Strictly follow referenced documentation; consult the user immediately if guidance conflicts or is incomplete.

## Service Boundaries & Dependencies
- Edit files under `services/kong-gateway/**` and related infrastructure configs when instructed.
- Ensure upstream URLs reference local services (agent-orchestrator, knowledge-rag, etc.) via docker-compose network names.
- Keep LiteLLM routing separate (port 4000) and ensure quotas are mirrored to Platform API.

## Testing & Verification
- Validate declarative config (e.g., `kong config db-import`).
- Run smoke tests hitting routed endpoints and verifying headers/plugins.
- Confirm metrics available at admin API and logs emitted as expected.

## Roadmap Tracking
- Reflect progress in [09-Roadmap](./docs/09-Roadmap.md); maintain one `in_progress` task, mark completion immediately when done.

## Clarifications & Collaboration
- If routing requirements or plugin behaviors are uncertain, ask the user rather than guessing.

## Security & Compliance
- Do not hardcode credentials; reference environment variables.
- Enforce tenant-aware rate limits and maintain audit logging via http-log plugin.

## Tooling Notes
- Use docker-compose stack for local validation. Keep Redis dependency healthy for rate limiting.
