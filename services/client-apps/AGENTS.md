# Agents — Client Apps (R1)

_Status: R1 UI build-out across Open WebUI, Admin, and Deloitte dashboards._

## Scope & Mission
- Configure and extend Open WebUI instances (Doc Chat, Code Chat) routed via Kong and LiteLLM.
- Implement Admin and Deloitte dashboards with Logto SSO, KPI visualizations, and tenant awareness.

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

## R1 Conventions
- Guardrails detect-only; enforce required headers via backend services.
- All API calls must go through Kong; LLM traffic via LiteLLM (OpenAI-compatible).
- Follow shared error envelope when building backend-facing adapters.

## Task & Commit Protocol
- Complete each roadmap item fully (UI + hooks + tests) before moving on; pause only for user feedback.
- Finish with Conventional Commit and push; set git user (Manan Ramnani) if missing.

## Context & Research Workflow
- Review service docs and existing UI/components first.
- Use **Context7 MCP** for framework/library docs (Next.js, TanStack Table, Open WebUI plugins, etc.).
- Use **Exa MCP (web_search)** for implementation patterns or troubleshooting.
- Use **Perplexity MCP** for high-level questions; follow official docs when in doubt.
- Log research findings prior to coding.
- Strictly comply with referenced documentation; raise questions to the user when ambiguity or conflicts appear.

## Service Boundaries & Dependencies
- Work inside `services/client-apps/**` unless explicitly coordinating with other services.
- Configure routing via Kong proxy URLs; never call downstream services directly.
- Handle Logto SSO flows; manage environment configuration entries documented in 06-Configuration.

## Testing & Verification
- Maintain unit tests for components; run integration/E2E tests (e.g., Playwright/Cypress) covering login, chat, dashboards.
- Verify builds (`pnpm build` or equivalent) and linting succeed.

## Roadmap Tracking
- Update statuses within [09-Roadmap](./docs/09-Roadmap.md): keep one task `in_progress`, then mark `completed` with notes if necessary.

## Clarifications & Collaboration
- Ask the user for clarification whenever KPIs, UI flows, or auth expectations are unclear; do not assume.

## Security & Compliance
- No secrets in front-end bundles; use environment variables and secure storage.
- Respect tenant isolation, avoid leaking data across tenants, and sanitise logs.

## Tooling Notes
- Use docker-compose or nx/pnpm workflows defined in repo for local development.
- Ensure environment variables mirror `.env.example` and Kong proxy routes exist before testing.

## Planning Notes
- When working on a plan or in planning mode you should ask the user any number of questions you like, and give them clear choices (upto 5) with a proper indication of which choice aligns with the architecture documentation
- Also when you receive a response from the user, ensure that you document that choice in a document DECISIONS.md in the parent platform at "C:\D.Coder-Droid\docs\project-docs\releases\R1\Decision.md" . Give a short super concise detail about the choice we made for what question
