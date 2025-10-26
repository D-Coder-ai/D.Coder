# 🏗️ D.Coder LLM Platform — R1 Architecture Guide

This document is the R1-local architecture reference. For scope and constraints, see `./PRD.md` and `./ARCHITECTURE_ADDENDUM.md` in this folder.

## 📋 Executive Summary

The D.Coder LLM Platform is an enterprise-grade, AI-native infrastructure designed specifically for building and deploying Large Language Model applications. After extensive research and analysis of cutting-edge open-source solutions, this architecture leverages specialized AI components that provide significant advantages over traditional approaches.

### Key Highlights
- 70% reduction in LLM costs through semantic caching and prompt compression
- 100% open-source stack with no vendor lock-in
- Enterprise-ready with multi-tenancy, audit trails, and SOC2-aligned architecture path
- MVP-deployable on a single Docker host, scalable to Kubernetes
- AI-native components purpose-built for LLM workloads

## 🎯 Platform Architecture Overview

### Core Design Principles
1. Macro-services Architecture: Services larger than microservices, each covering a full business domain
2. AI-First Design: Every component optimized for LLM workloads
3. Open Source Foundation: No proprietary dependencies
4. Progressive Enhancement: Start simple (Docker), scale to complexity (Kubernetes)
5. Developer Experience: Visual tools for non-engineers, familiar frameworks for developers

> R1 defaults: BYO LLM per tenant; no local inference; SSO via Logto; feature flags via Flagsmith; DB-per-tenant isolation; quotas at Kong+API; alert-only guardrails; providers supported: OpenAI, Anthropic, Google/Vertex, Groq; no automatic provider failover in R1.

## 🏛️ Service Architecture

### 7 Core Macro-Services + Infrastructure

#### 1. 🔮 Hybrid Gateway Architecture (Ports 8000 & 4000)

**Design:** Split gateway responsibilities between Kong Gateway (platform APIs) and LiteLLM Proxy (LLM traffic) with shared observability.

##### 1a. Kong Gateway (Port 8000) — Platform Service Routing
Purpose: General-purpose API gateway for macro-services.

Key Features:
- Service routing (Agent Orchestrator, Knowledge & RAG, Integrations, LLMOps)
- Rate limiting, request/response transforms, auth enforcement
- Platform quotas mirrored from LiteLLM `quota.updated` events surfaced through the Platform API
- Observability and tracing via OTel exporters

Technology Stack:
- Kong Gateway OSS
- Redis for rate limiting counters
- Declarative configuration rendered from `services/kong-gateway/config`

##### 1b. LiteLLM Proxy (Port 4000) — LLM Gateway
Purpose: Specialized gateway for LLM provider traffic with caching and compression.

Key Features:
- Multi-LLM routing (OpenAI, Anthropic, Google/Vertex, Groq)
- Redis-backed semantic caching (LiteLLM native)
- Optional prompt compression via middleware at `services/litellm-proxy/middleware/`
- Cost and usage tracking with virtual keys
- Guardrails hooks (alert-only in R1)

Technology Stack:
- LiteLLM Proxy (MIT)
- Redis for cache + rate limits
- PostgreSQL for virtual keys

**Request Flow:**
```
Client → Platform API ─┬─→ Kong Gateway → Platform Services
                       └─→ LiteLLM Proxy → LLM Providers
```

> R1: LiteLLM handles caching and compression; Kong focuses on platform APIs. No automatic provider failover (manual only). Quotas enforced at LiteLLM and mirrored in Platform API. Guardrails remain alert-only. See `docs/project-docs/updates/hybrid-gateway-architecture-litellm-integration.md`.

Local orchestration runs from `infrastructure/docker-compose.base.yml` (with optional `docker-compose.dev.yml` overlays). Per-service compose files under `services/*/docker-compose.yml` are limited to isolated development and must not diverge from the base stack.

#### 2. 🧪 LLMOps Platform Service (Port 8081)
Purpose: Prompt engineering, experimentation, and evaluation

Key Features:
- Visual prompt playground
- A/B testing for prompts
- Evaluation frameworks (LLM-as-judge, custom metrics)
- Version control for prompts
- Experiment tracking
- Human-in-the-loop evaluation

Technology Stack:
- Primary: Agenta (MIT)
- Alternative: Pezzo (Apache 2.0)
- MLFlow for experiment tracking
- Langfuse for LLM observability

Why Agenta:
- 10x faster prompt iteration with visual tools
- Built-in evaluation without custom code
- Production deployment capabilities

#### 3. 🏢 Platform API Service (FastAPI - Port 8082)
Purpose: Core platform capabilities and governance

Key Features:
- Multi-tenancy management (org/group/user)
- Authentication and authorization (ABAC)
- Usage tracking and billing
- Feature flags and quotas
- Audit trail with signed hash chains
- Deloitte IP protection (envelope encryption design for R2+)

Technology Stack:
- FastAPI (Python)
- Logto (R1 default) or Keycloak
- Casbin for ABAC
- PostgreSQL for data
- Redis for caching

Security Features:
- AES-GCM envelope encryption for prompts (R2+ design)
- Runtime-only decryption (R2+)
- Complete audit trails
- OIDC/SSO support

> Tenant isolation strategy: Database per tenant in R1; see `./CONFIGURATION.md`. Feature flags via Flagsmith.

#### 4. 🤖 Agent Orchestration Service (FastAPI - Port 8083)
Purpose: Durable workflow execution for AI agents

Key Features:
- Agent graphs (plan/execute/review cycles)
- Tool routing and MCP integration
- Durable execution with automatic recovery
- Event-driven architecture
- Integration with external tools

Technology Stack:
- FastAPI with Temporal workflows
- NATS JetStream for events
- LangGraph for agent orchestration
- Integration with Kong AI Gateway

Why Temporal:
- Never lose agent state
- Automatic retry and recovery
- Perfect for long-running AI workflows

#### 5. 📚 Knowledge & RAG Service (FastAPI - Port 8084)
Purpose: Document processing and semantic search

Key Features:
- Document crawling and parsing
- Code indexing (OOTB + customizations)
- Semantic search with hybrid retrieval
- RAG pipeline with grounding
- Multi-modal support (text, code, images)

Technology Stack:
- FastAPI backend
- MVP: PostgreSQL + pgvector
- Scale: Milvus
- LlamaIndex for RAG orchestration
- Unstructured.io for parsing

Vector Database Strategy:
- Start with pgvector (simple, integrated)
- Migrate to Milvus when >100M vectors
- GPU acceleration available with Milvus

#### 6. 🔌 Integrations Service (FastAPI - Port 8085)

Purpose: External system connectivity



Key Features:

- JIRA agent (story analysis, point estimation)

- Bitbucket code review agent

- Confluence/SharePoint documentation sync

- MCP tool exposition

- Webhook handlers

- Custom API connectors



Technology Stack:

- FastAPI with async workers

- NATS for event distribution

- Celery for background tasks

- Redis for task queue



> Integrations follow a plugin architecture; see `./PLUGIN_ARCHITECTURE.md`. Plugins enabled per tenant via Flagsmith.



#### 7. 🖥️ Client Applications (Ports 3000-3004)

Purpose: User interfaces and developer tools



Components:

- Chat Interface: Open WebUI

  - Pipeline-based architecture

  - Customizable with plugins

  - Two instances: Doc Chat & Code Chat

- Admin Dashboard: Next.js + TanStack Table

  - Client administration

  - Usage monitoring

  - Cost tracking

- Deloitte Dashboard: Internal monitoring

- IntelliJ Plugin: Backend API



UI Technology Choices:

- Open WebUI (most popular, extensible)

- Alternative: LibreChat

- Alternative: Lobe Chat



## 💾 Data Architecture



### Primary Data Stores



1. PostgreSQL (Port 5432)

   - Main relational database

   - Stores: tenancy, users, configurations, audit logs

   - Extensions: pgvector for embeddings (MVP)



2. Redis (Port 6379)

   - Caching layer

   - Session storage

   - Rate limiting counters

   - Semantic cache for LiteLLM proxy



3. MinIO (Ports 9000/9001)

   - S3-compatible object storage

   - Document storage

   - Model artifacts (MLFlow)

   - Backup archives



4. Milvus (Future - Port 19530)

   - Production vector database

   - Billion+ vector scale

   - GPU acceleration support



> Tenant isolation: Database per tenant (R1). Backups/DR targets: daily encrypted backups; RPO 24h, RTO 4h. See release addendum for evolutions.



## 📁 Repository Structure (R1)



```

llm-platform/

├── apps/

│   ├── gateways/

│   │   ├── kong/

│   │   └── litellm-proxy/

│   ├── agenta/

│   ├── platform-api/

│   ├── agent-orchestrator/

│   ├── knowledge-rag/

│   ├── integrations/

│   ├── open-webui/

│   └── admin-dashboard/

├── infra/

│   ├── docker-compose.yml

│   ├── docker-compose.dev.yml

│   ├── kong/

│   ├── logto/

│   ├── mlflow/

│   └── observability/

└── docs/

    └── project-docs/

        └── releases/

            └── R1/

```



## 🚀 Implementation Roadmap (Phases snapshot)

- Phase 1: Foundation (Gateway, Stores, Auth)

- Phase 2: LLMOps Platform (Agenta, MLFlow, Langfuse)

- Phase 3: Core Services (Platform API, Orchestrator, RAG)

- Phase 4: User Interfaces (Open WebUI, Dashboards)

- Phase 5: Advanced Features (Integrations, Prompt encryption planning)

- Phase 6: Production Hardening



## 📚 Additional Resources

- PRD: `./PRD.md`

- Architecture Addendum: `./ARCHITECTURE_ADDENDUM.md`

- Plugin Architecture: `./PLUGIN_ARCHITECTURE.md`

- Configuration Model: `./CONFIGURATION.md`

- Guardrails Policy: `./GUARDRAILS_AND_DLP.md`

- Prompt Encryption (R2 plan): `./PROMPT_ENCRYPTION_R2_PLAN.md`




