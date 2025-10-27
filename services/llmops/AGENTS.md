# Agents — LLMOps (R1)

_Status: R1 experimentation stack — Agenta, MLFlow, Langfuse._

## Scope & Mission
- Deploy and configure Agenta for prompt experimentation, MLFlow for tracking/artifacts, and Langfuse for LLM observability.
- Provide foundational experiment flows and integrations with platform services/LiteLLM as needed.

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

## R1 Conventions
- Guardrails detect-only; respect required headers when interacting with platform services.
- Maintain observability (metrics/traces) for experiments and prompt runs.

## Task & Commit Protocol
- Complete roadmap items sequentially (deployment, MLFlow integration, Langfuse wiring, experiment flow). Pause only for user clarifications.
- Use Conventional Commits; push after staging; configure git user (Manan Ramnani) if needed.

## Context & Research Workflow
- Review service docs, upstream tool docs, and infrastructure expectations before changes.
- Use **Context7 MCP** for Agenta, MLFlow, Langfuse, and related libraries.
- Use **Exa MCP (web_search)** for deployment patterns or troubleshooting.
- Use **Perplexity MCP** for high-level context; follow official docs if discrepancies occur.
- Capture research conclusions before implementing.
- Strictly follow referenced documentation; escalate ambiguities or conflicts to the user before coding.

## Service Boundaries & Dependencies
- Work within `services/llmops/**` unless coordination is required.
- Connect to LiteLLM for model calls from Agenta; store artifacts in MinIO per configuration.
- Integrate with observability stack defined in infrastructure.

## Testing & Verification
- Smoke-test UI reachability, MLFlow run logging, Langfuse trace ingestion.
- Add automated tests or scripts where feasible to validate experiment flows.

## Roadmap Tracking
- Update progress markers in [09-Roadmap](./docs/09-Roadmap.md), keeping one `in_progress` item and marking completion promptly.

## Clarifications & Collaboration
- When unsure about experiment scope, metrics, or integrations, ask the user for guidance before coding.

## Security & Compliance
- Keep credentials out of source; rely on environment variables and secure configuration.
- Ensure tenant separation in tracking stores; redact sensitive prompt data in logs where needed.

## Tooling Notes
- Use docker-compose overlays for MLFlow, MinIO, Langfuse as documented.
- Ensure networking and ports align with infrastructure configuration.

## Planning Notes
- When working on a plan or in planning mode you should ask the user any number of questions you like, and give them clear choices (upto 5) with a proper indication of which choice aligns with the architecture documentation
- Also when you receive a response from the user, ensure that you document that choice in a document DECISIONS.md in the parent platform at "C:\D.Coder-Droid\docs\project-docs\releases\R1\Decision.md" . Give a short super concise detail about the choice we made for what question
