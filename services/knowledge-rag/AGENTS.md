# Agents — Knowledge & RAG (R1)

_Status: Ready for ingestion and retrieval implementation aligned with R1 scope._

## Scope & Mission
- Deliver ingestion, parsing, indexing, and hybrid retrieval for documents/code to support grounded responses.
- Emit ingestion/index lifecycle events and maintain tenant-isolated stores (PostgreSQL + pgvector, MinIO).

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
- Guardrails detect-only; routing through Kong/LiteLLM mirrors quotas into Platform API.
- Mandatory headers and error envelope per Service Contracts.
- Events must use shared envelope and NATS JetStream subjects (`ingestion.*`, `index.*`).

## Task & Commit Protocol
- Complete roadmap items end-to-end before switching tasks. Only pause for user clarifications.
- After finishing, stage changes, create Conventional Commit, push. Configure git user (Manan Ramnani) if missing.

## Context & Research Workflow
- Collect context from service docs and existing code before coding.
- Use **Context7 MCP** for Unstructured, pgvector, LlamaIndex, or other dependency documentation.
- Use **Exa MCP (web_search)** for best practices and troubleshooting.
- Use **Perplexity MCP** for supplementary background; defer to official docs when conflicts arise.
- Summarize research in task notes prior to implementation.
- Strictly adhere to referenced documentation; escalate to the user whenever expectations are unclear or conflicting.

## Service Boundaries & Dependencies
- Work within `services/knowledge-rag/**` unless instructed otherwise.
- Ingestion pipeline: Unstructured parsing, chunking, embeddings (via LiteLLM or local).
- Storage: PostgreSQL + pgvector; artifact storage in MinIO.
- Outbound HTTP passes through Kong gateway; embedding/model calls may use LiteLLM Proxy.

## Testing & Verification
- Maintain unit tests for chunking, embedding adapters, ranking.
- Execute integration tests covering ingestion→index→search.
- Provide E2E proof (sample corpus) and ensure health/metrics endpoints succeed.

## Roadmap Tracking
- Update task states directly in [09-Roadmap](./docs/09-Roadmap.md); only one task should be `in_progress` at a time.

## Clarifications & Collaboration
- When requirements or data sources are ambiguous, ask the user immediately—no assumptions.

## Security & Compliance
- Respect tenant isolation; avoid storing secrets; redact sensitive document content in logs.
- Guardrails detect-only; log alerts for review.

## Tooling Notes
- Ensure docker-compose dependencies (PostgreSQL, MinIO, Redis) are running.
- Validate pgvector extension is enabled and migrations cover required schemas.
