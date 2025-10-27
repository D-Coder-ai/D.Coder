# Agents — R1 Overview

_Status: R1 — early development; partial work completed._

## References
- [PRD.md](mdc:docs/project-docs/releases/R1/PRD.md)
- [AGENT_ENGINEERING_BRIEF.md](mdc:docs/project-docs/releases/R1/AGENT_ENGINEERING_BRIEF.md)
- [ARCHITECTURE.md](mdc:docs/project-docs/releases/R1/ARCHITECTURE.md)
- [ARCHITECTURE_ADDENDUM.md](mdc:docs/project-docs/releases/R1/ARCHITECTURE_ADDENDUM.md)
- [SERVICE_CONTRACTS.md](mdc:docs/project-docs/releases/R1/SERVICE_CONTRACTS.md)
- [PLUGIN_ARCHITECTURE.md](mdc:docs/project-docs/releases/R1/PLUGIN_ARCHITECTURE.md)
- [CONFIGURATION.md](mdc:docs/project-docs/releases/R1/CONFIGURATION.md)

## Agent Taxonomy (High Level)
- **Agent Orchestrator**: Workflow entrypoints, tool routing, and NATS subject coordination. See [services/agent-orchestrator/README.md](mdc:services/agent-orchestrator/README.md)
- **Knowledge & RAG**: Ingestion, pgvector indexing, retrieval APIs for Doc/Code Chat. See [services/knowledge-rag/README.md](mdc:services/knowledge-rag/README.md)
- **Integrations**: Plugin catalog scaffolding with per-tenant enable/disable controls. See [services/integrations/README.md](mdc:services/integrations/README.md)
- **Client Apps**: Open WebUI surfaces (Doc Chat, Code Chat) and admin dashboards. See [services/client-apps/README.md](mdc:services/client-apps/README.md)
- **AI Gateway**: Kong + LiteLLM proxy for routing, semantic cache, prompt compression, and guardrail alerts. See [services/kong-gateway/README.md](mdc:services/kong-gateway/README.md), [services/litellm-proxy/README.md](mdc:services/litellm-proxy/README.md)
- **Platform API**: Tenancy, ABAC, quotas/usage, provider configuration, feature flags. See [services/platform-api/README.md](mdc:services/platform-api/README.md)

Refer to [AGENT_ENGINEERING_BRIEF.md](mdc:docs/project-docs/releases/R1/AGENT_ENGINEERING_BRIEF.md) for the full R1 scope, definition of done, and handoff expectations.

## R1 Conventions
- Guardrails operate in detect-only mode; quotas enforced at the AI gateway and mirrored in Platform API usage tracking.
- Cross-service headers, error envelopes, and versioning follow [SERVICE_CONTRACTS.md](mdc:docs/project-docs/releases/R1/SERVICE_CONTRACTS.md).

#### Task / TODO Completion Protocol
**When implementing any task / TODO :**
1. Work continuously until ALL planned TODOs are completed
2. Complete ALL development required for that task
3. Stop only if user action is required (approvals, external inputs)
4. DO NOT stop mid-implementation for documentation or summaries
5. Reasoning: Maintains clean context, prevents scope creep, enables better tracing

#### Automatic Commit Protocol
**On task / TODO completion:**
```bash
# Automatic actions required:
1. Stage all changes made during this subtask
2. Create commit using Conventional Commits format
3. Commit message format:
   - Type: feat|fix|refactor|docs|test|chore
   - Summary: Concise changelist of all work done
4. Push to remote automatically

# Example:
git add .
git commit -m "feat: implement JWT authentication

- Added bcrypt password hashing
- Implemented JWT token generation
- Created auth middleware for protected routes
- Added unit tests for auth functions"
git push origin <current-branch>

# If user.name/user.email not set:
git config user.name "Manan Ramnani"
git config user.email "ramnani.manan@gmail.com"
```

#### Context Gathering Protocol
**Before starting any task/TODO:**
1. Gather all details only exactly related to that task
2. Identify ALL dependencies from task description
3. Gather context systematically:
   - Context7 MCP: Official docs for libraries involved
   - Exa MCP: Best practices, recent discussions
   - Existing implementation: Related code files
   - Project docs: Architecture, contracts, configuration
4. Create mental checklist of what needs verification
5. Only then begin implementation planning

### Research-First Development
**Standing order: Research before assumptions**
- Use Context7 MCP for ANY library-specific question
- Use Exa MCP for architectural patterns or best practices
- Use web_search as last resort
- Document what you researched and what you found
- Update task with research findings before implementation

