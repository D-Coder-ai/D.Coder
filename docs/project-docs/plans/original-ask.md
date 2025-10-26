# Original Client Ask

The following captures the original request and background provided for the Deloitte enterprise agentic framework. It excludes any generated plans or derived documentation.

## Background & Objectives
- Application developed by Deloitte USI targeting a large framework of Generative AI tools for the insurance industry, beginning with Guidewire Insurance Suite applications.
- Solution must be easy for clients to deploy while ensuring no code, secrets, or PII leave the client’s ecosystem.
- Deployment flexibility: Deloitte-hosted or client-hosted using their own enterprise LLM subscriptions.
- Support differentiated user allocations (query counts, task types), scalability, SOC2 compliance, full audit trail with end-to-end traceability, and archival of complete LLM conversations.
- Deloitte requires usage metrics, stability indicators, and cost insights at user, group, and organization levels across clients.
- System prompts for services (especially coding and USB agents) are Deloitte IP and must be encrypted, accessible only at runtime, and resilient against MITM/proxy/prompt-injection attacks.
- Need feature management and A/B testing; ability to revoke client access upon offboarding, preventing continued use and code visibility.
- Deloitte must maintain master control to revoke access for any client, group, or user.
- Integration with client IdP/LDAP/MFA/SSO required.
- Services may be white-labeled open-source applications or built from scratch.

## Targeted Features & Components
1. **IntelliJ Coding Agent (Guidewire Studio Plugin / Cline wrapper)** – Gen AI coding agent with subagents, orchestration, and specialized tooling; client-facing. (Beind developed separately)
2. **Crawler** – Ingest Guidewire documentation across domains/versions and produce structured outputs; backend service. (Developed separately)
3. **Code Chat** – ChatGPT-like web app for codebase conversations with persona-driven responses; client-facing.
4. **Doc Chat** – ChatGPT-like web app for Guidewire documentation queries with structured answers; client-facing.
5. **Doc Index** – Agentic RAG/indexing consumed by Doc Chat and Coding Agent for grounded development plans; backend service.
6. **Code Index** – Agentic RAG/indexing on existing code (OOTB plus customizations) to provide baseline patterns for coding agent and code chat; backend service.
7. **JIRA Agent** – AI agent with dedicated Jira account for functional/technical analysis and story-point planning, triggered via Jira mentions.
8. **Code Review Agent** – AI agent with Bitbucket access to review PRs, operate via sandbox checkout, and update Jira when reviews complete; shares Jira account with Jira agent.
9. **Confluence/SharePoint Agent** – AI agent maintaining technical docs in Confluence/SharePoint, triggered on PR merges, exposing an MCP service for coding agents and chats.
10. **Admin Dashboard** – Client-facing admin portal for access control, usage/cost monitoring, and operational oversight.
11. **Deloitte Dashboard** – Internal view for Deloitte to monitor client usage, errors, metrics, and costs.

## Architectural Principles & Constraints
- **Macro-services** (practical DDD): services larger than typical microservices, each covering a full business domain.
- **Service Splitting Rule**: split only when independent scaling, significantly different change cadence, or distinct technology stack is required.
- **Communication**: synchronous via HTTP REST or gRPC (prefer gRPC); asynchronous via event-driven architecture.
- **Platform Infrastructure**:
  - API Gateway and Service Mesh.
  - (Future scope) Helm charts for distribution (beta readiness).
  - (Future scope) Kubernetes-compliant framework for broad deployability.
  - OpenTelemetry for observability and monitoring.
- **Compliance & Security**: SOC2 readiness; audit trail for all interactions with complete archival; Deloitte IP protection with encrypted prompts only available at runtime.
- **Control & Governance**: Deloitte retains master control over client/group/user access and must prevent post-offboarding usage; clients cannot view or reverse engineer Deloitte code.
