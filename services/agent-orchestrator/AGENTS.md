# Agents — Agent Orchestrator (R1)

_Status: Ready for focused implementation; follow R1 conventions._

## Scope & Mission
- Build and maintain durable agent workflows using Temporal + LangGraph with NATS-driven signaling.
- Ensure plan/act/review loops function end-to-end, emitting `workflow.*` events and calling downstream services through Kong and LiteLLM.

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
- Guardrails operate in detect-only mode; quotas enforced at gateway and mirrored in Platform API.
- Every request includes headers: `X-Request-Id`, `X-Tenant-Id`, `X-Platform-Id`, `X-User-Id`, `X-Trace-Id`, optional `Idempotency-Key`.
- Errors follow `{ "error": { "code", "message", "details" } }`; events use the shared envelope.

## Task & Commit Protocol
- Complete all steps of a roadmap item before moving on; do not pause mid-task unless waiting on user input.
- On completion: stage changes, craft Conventional Commit (`feat|fix|refactor|docs|test|chore`), push to current branch. Configure git user (Manan Ramnani) if unset.

## Context & Research Workflow
- Before coding, gather only task-relevant context from docs and existing code.
- Use **Context7 MCP** for official library/tool documentation; cite versions used.
- Use **Exa MCP (web_search)** when patterns or troubleshooting guidance is needed for dependencies.
- Use **Perplexity MCP** for broader background questions. Treat it as supplemental; defer to official docs if conflicts arise.
- Document research findings in task notes before implementation.
- Strictly follow referenced documentation; if guidance conflicts, pause and ask the user before proceeding.

## Service Boundaries & Dependencies
- Modify only files under `services/agent-orchestrator/**` unless the task explicitly spans multiple services.
- Temporal workflows, LangGraph nodes, and NATS JetStream integrations belong here.
- All outbound HTTP calls go through Kong Gateway; LLM calls use LiteLLM Proxy (port 4000).
- Propagate tenant/auth headers on every outbound call.

## Testing & Verification
- Run and update unit tests (workflow nodes, adapters), integration tests (Temporal/NATS), and E2E samples that exercise plan→act→review flows.
- Ensure `/metrics` and health endpoints stay green; fix lint/type checks before completion.

## Roadmap Tracking
- Update status markers inside [09-Roadmap](./docs/09-Roadmap.md) as you progress: mark one item `in_progress`, complete it, then mark `completed` with brief notes if required.

## Clarifications & Collaboration
- If requirements are unclear or assumptions are needed, ask the user as many questions as necessary before coding. Do not guess.

## Security & Compliance
- No secrets in code or logs; respect tenant isolation. Maintain structured JSON logging with correlation IDs. Guardrails remain detect-only; record alerts.

## Tooling Notes
- Use docker-compose services for Temporal, NATS, Redis. Validate event subjects (`workflow.*`) and Temporal namespaces before deployment.
