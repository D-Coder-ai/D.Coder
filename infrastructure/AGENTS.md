# Agents — Infrastructure (R1)

_Status: R1 environment orchestration — docker-compose, policies, shared services._

## Scope & Mission
- Maintain infrastructure automation for local/CI environments: docker-compose stacks, observability, messaging, storage, and policy artifacts.
- Ensure platform services have healthy dependencies (PostgreSQL, Redis, NATS, Temporal, Kong, LiteLLM, MinIO, Logto, Flagsmith, observability suite).

## References
- [Infrastructure README](./README.md)
- [`docker-compose.base.yml`](./docker-compose.base.yml)
- [`docker-compose.dev.yml`](./docker-compose.dev.yml)
- Policies under [`./policies`](./policies/)
- Observability stack docs (`./observability/`)
- [Platform PRD](../docs/project-docs/releases/R1/PRD.md)
- [Architecture](../docs/project-docs/releases/R1/ARCHITECTURE.md)
- [Configuration Model](../docs/project-docs/releases/R1/CONFIGURATION.md)

## R1 Conventions
- Guardrails detect-only; ensure supporting services surface required headers/metrics for application services.
- Infrastructure changes must not break declarative conventions or service contracts.

## Task & Commit Protocol
- Complete each infra roadmap/task fully before moving on (compose updates, policy changes, docs coordination). Pause only for user direction.
- After finishing, stage, Conventional Commit, push; configure git user (Manan Ramnani) if needed.

## Context & Research Workflow
- Review compose files, policies, and service documentation prior to changes.
- Use **Context7 MCP** for official docs of infra components (Docker Compose, NATS, Redis, MinIO, Logto, Flagsmith, Temporal, etc.).
- Use **Exa MCP (web_search)** for best practices or troubleshooting orchestration issues.
- Use **Perplexity MCP** for supplementary background; defer to official docs when conflicts arise.
- Record research insights before implementing changes.
- Strictly follow referenced documentation; whenever expectations are ambiguous or conflicting, pause and ask the user.

## Boundaries & Responsibilities
- Limit modifications to `infrastructure/**` unless cross-service adjustments are explicitly requested.
- Coordinate versioning and configuration with services (e.g., ensure Kong/LiteLLM ports align with service expectations).
- Keep environment variables in sync with `.env.example`; never commit secrets.

## Testing & Verification
- Validate docker-compose stacks (`docker compose up`, health checks) and confirm dependent services respond on expected ports.
- Run smoke checks (health endpoints, metrics) for each macro service after infra changes.

## Roadmap Tracking
- When an infra task links to a service roadmap, update the corresponding service document and maintain a local checklist (if applicable). Communicate status updates to the user.

## Clarifications & Collaboration
- If infrastructure requirements or resource allocations are unclear, ask the user for confirmation before proceeding.

## Security & Compliance
- Respect provider allowlists, network segmentation, and storage encryption policies in configuration.
- Ensure logs and backups follow retention policies described in R1 documents.

## Tooling Notes
- Use make/compose scripts defined in repo; keep container versions aligned with service docs.
- Monitor resource usage and adjust compose overrides responsibly.
