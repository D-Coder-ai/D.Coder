# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

D.Coder LLM Platform is an enterprise-grade, AI-native infrastructure designed for building and deploying Large Language Model applications, specifically targeting Deloitte's insurance industry needs (Guidewire Insurance Suite applications). The platform emphasizes:

- **70% reduction in LLM costs** through semantic caching and prompt compression
- **100% open-source** stack with no vendor lock-in
- **Enterprise-ready** with multi-tenancy, SOC2 compliance, and full audit trails
- **Deloitte IP protection** with encrypted prompts accessible only at runtime

## Architecture Principles

1. **Macro-services Architecture**: Services larger than microservices, each covering a full business domain
2. **Service Splitting Rule**: Split only when independent scaling, significantly different change cadence, or distinct technology stack is required
3. **AI-First Design**: Every component optimized for LLM workloads
4. **Progressive Enhancement**: Start simple (Docker), scale to complexity (Kubernetes)
5. **Security by Design**: Envelope encryption for prompts, audit trails with signed hash chains, ABAC authorization

## Core Services Architecture

The platform consists of 7 macro-services:

1. **AI Gateway Service** (Kong AI Gateway - Port 8000): Multi-LLM routing, semantic caching, prompt compression, rate limiting
2. **LLMOps Platform Service** (Port 8081): Prompt engineering, A/B testing, evaluation frameworks (Agenta + MLFlow + Langfuse)
3. **Platform API Service** (FastAPI - Port 8082): Multi-tenancy, authentication, usage tracking, audit trails, feature flags
4. **Agent Orchestration Service** (FastAPI - Port 8083): Durable workflows with Temporal, LangGraph agent graphs, tool routing
5. **Knowledge & RAG Service** (FastAPI - Port 8084): Document processing, semantic search, pgvector (MVP) → Milvus (scale)
6. **Integrations Service** (FastAPI - Port 8085): JIRA agent, Bitbucket code review, Confluence/SharePoint sync
7. **Client Applications** (Ports 3000-3004): Open WebUI instances, Admin Dashboard (Next.js), Deloitte Dashboard

### Infrastructure Services

- **Observability** (Port 8086): Grafana Loki, Prometheus, Grafana, OpenTelemetry, Langfuse
- **Data Stores**: PostgreSQL (5432), Redis (6379), MinIO (9000/9001), Milvus (future - 19530)
- **Authentication**: Logto or Keycloak with OIDC/SSO support

## Development Commands

```bash
# Initial setup
docker-compose up -d

# Development mode with overrides
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View service logs
docker-compose logs -f [service-name]

# Check service health
docker-compose ps

# Rebuild specific service
docker-compose up -d --build [service-name]

# Stop all services
docker-compose down

# Remove volumes (careful - data loss)
docker-compose down -v
```

## Repository Structure

```
D.Coder/
├── apps/                      # Application services (when implemented)
│   ├── kong-ai-gateway/       # AI Gateway configuration
│   ├── platform-api/          # Core platform API (FastAPI)
│   ├── agent-orchestrator/    # Agent workflows (FastAPI + Temporal)
│   ├── knowledge-rag/         # RAG service (FastAPI + LlamaIndex)
│   ├── integrations/          # External connectors (FastAPI)
│   └── client-apps/           # UI applications
├── infra/                     # Infrastructure configuration (future)
│   ├── docker-compose.yml
│   ├── kong/
│   ├── observability/
│   └── data/
├── packages/                  # Shared libraries (future)
│   ├── python/common/
│   └── js/ui-components/
├── docs/                      # Documentation
│   ├── PLATFORM_ARCHITECTURE.md  # Complete architecture & implementation guide
│   └── project-docs/
│       └── plans/
│           └── original-ask.md   # Original Deloitte requirements
└── .claude/agents/           # Claude Code agent configurations
    ├── project-manager.md
    ├── cto-chief-architect.md
    └── technical-product-manager.md
```

## Specialized Agents

This repository has three specialized Claude Code agents configured. Use them appropriately:

### 1. project-manager Agent (Red)
**Use when:**
- Validating changes against original requirements (docs/project-docs/plans/original-ask.md)
- Updating project documentation
- Managing Linear project tracking (projects → epics → stories → issues)
- Checking for scope creep or requirement drift
- Need to ensure project coherence with original vision

**Model:** Sonnet

### 2. cto-chief-architect Agent (Blue)
**Use when:**
- Designing system architecture or cross-service integrations
- Making technology stack decisions (frameworks, libraries)
- Defining communication protocols between services
- Researching OSS frameworks (uses Context7, Tavily, Exacode)
- Reviewing architectural alignment across services
- Need strategic technical guidance

**Model:** Opus

### 3. technical-product-manager Agent (Green)
**Use when:**
- Creating/updating HLDs, PRDs, README, INTEGRATION_GUIDE.md
- Documenting service APIs and integration patterns
- Maintaining AGENTS.md or CLAUDE.md files
- After implementing new services or significant features
- Need to synchronize documentation with code changes

**Model:** Inherit

## Security Requirements

### Deloitte IP Protection
- **System prompts are Deloitte IP**: Must be encrypted using envelope encryption (AES-GCM)
- **Runtime-only decryption**: Prompts accessible only during execution
- **No visibility to clients**: Clients cannot view or reverse engineer Deloitte code/prompts
- **Audit trail**: All LLM interactions must be logged with cryptographic signatures
- **Master control**: Deloitte retains ability to revoke access for any client/group/user

### Authentication & Authorization
- Integrate with client IdP/LDAP/MFA/SSO
- ABAC (Attribute-Based Access Control) using Casbin
- Multi-tenancy at org/group/user levels
- Feature flags and quota enforcement per tenant

### Compliance
- SOC2 compliant architecture
- Complete audit trail with end-to-end traceability
- Archive all LLM conversations with metadata
- Usage metrics at user, group, and organization levels

## Key Documentation

- **docs/PLATFORM_ARCHITECTURE.md**: Complete architecture overview, technology choices, implementation roadmap, cost analysis
- **docs/project-docs/plans/original-ask.md**: Original Deloitte requirements and constraints (source of truth)

## Technology Stack Highlights

- **Gateway**: Kong AI Gateway 3.11+ (AI-native routing, caching, prompt compression)
- **Backend**: FastAPI (Python) for all API services
- **Orchestration**: Temporal for durable workflows, NATS JetStream for events
- **LLM Ops**: Agenta (prompt playground), MLFlow (experiments), Langfuse (observability)
- **RAG**: LlamaIndex orchestration, pgvector (MVP), Milvus (production scale)
- **UI**: Open WebUI (chat), Next.js (dashboards)
- **Observability**: Grafana Loki (logs), Prometheus (metrics), OpenTelemetry (traces)
- **Auth**: Logto (modern) or Keycloak (enterprise LDAP/AD)

## Implementation Status

**Current Phase**: Architecture & Planning
- Architecture documentation complete (docs/PLATFORM_ARCHITECTURE.md)
- Requirements captured (docs/project-docs/plans/original-ask.md)
- Agent configurations in place (.claude/agents/)
- No code implementation yet

**Next Steps** (per PLATFORM_ARCHITECTURE.md Phase 1):
1. Deploy Kong AI Gateway with initial configuration
2. Setup PostgreSQL, Redis, MinIO
3. Configure Logto authentication
4. Create Docker networking and environment variables

## Notes

- Prefer macro-services over microservices to reduce operational complexity
- Always validate changes against original-ask.md to prevent scope creep
- Use the specialized agents for their domains - they have specific responsibilities
- Security and IP protection are non-negotiable requirements
- Target deployment: Docker Compose (MVP), Kubernetes (production scale)

## Task Master AI Instructions
**Import Task Master's development workflow commands and guidelines, treat as if import is in the main CLAUDE.md file.**
@./.taskmaster/CLAUDE.md
