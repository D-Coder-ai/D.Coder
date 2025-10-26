# D.Coder LLM Platform

> Enterprise-grade, AI-native infrastructure for building and deploying Large Language Model applications

[![License](https://img.shields.io/badge/license-PROPRIETARY-red.svg)](LICENSE)
[![Node](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Nx](https://img.shields.io/badge/monorepo-Nx-blue)](https://nx.dev)

## 🎯 Overview

D.Coder is a comprehensive LLM platform designed specifically for Deloitte's insurance industry needs, with a focus on Guidewire Insurance Suite applications. The platform provides:

- **70% reduction in LLM costs** through semantic caching and prompt compression
- **100% open-source stack** with no vendor lock-in
- **Enterprise-ready** with multi-tenancy, SOC2 compliance, and full audit trails
- **Deloitte IP protection** with encrypted prompts accessible only at runtime

## 🏗️ Architecture

### Hybrid Gateway Design

- **Kong Gateway** (Port 8000): Platform service routing, rate limiting, observability
- **LiteLLM Proxy** (Port 4000): LLM-native routing with Redis caching, prompt compression, cost-based routing

### Core Services

| Service | Port | Description |
|---------|------|-------------|
| **Platform API** | 8082 | Multi-tenancy, authentication, quotas, governance |
| **Agent Orchestrator** | 8083 | Durable workflows with Temporal & LangGraph |
| **Knowledge & RAG** | 8084 | Document processing, semantic search (pgvector → Milvus) |
| **Integrations** | 8085 | JIRA, Bitbucket, Confluence connectors |
| **LLMOps** | 8081 | Prompt engineering, A/B testing, evaluation (Agenta + MLFlow) |

### Infrastructure

- PostgreSQL (5432), Redis (6379), MinIO (9000/9001), NATS (4222)
- Temporal (7233), Logto (3001/3002), Flagsmith (8090)
- Prometheus (9090), Grafana (3005), Loki (3100)

## 🚀 Quick Start

### Prerequisites

- Node.js 20+ and pnpm 8+
- Docker & Docker Compose
- Python 3.11+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/deloitte/dcoder-platform.git
cd dcoder-platform

# Install dependencies
pnpm install

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Start infrastructure
make infra-up

# Start full stack (optional)
docker-compose --profile full up -d
```

### Verify Installation

```bash
# Check infrastructure status
make status

# View logs
make infra-logs

# Test connectivity
curl http://localhost:8000/health  # Kong
curl http://localhost:4000/health  # LiteLLM
curl http://localhost:8082/health  # Platform API
```

## 📁 Repository Structure

```
D.Coder/
├── services/               # All application services
│   ├── kong-gateway/       # Kong platform gateway
│   ├── litellm-proxy/      # LiteLLM LLM gateway
│   ├── platform-api/       # Platform API service
│   ├── agent-orchestrator/ # Agent orchestration
│   ├── knowledge-rag/      # RAG service
│   ├── integrations/       # External integrations
│   ├── llmops/            # LLMOps platform
│   └── client-apps/       # Client applications
│
├── packages/              # Shared libraries
│   ├── python/            # Python packages
│   │   └── dcoder-common/ # Shared Python utilities
│   └── typescript/        # TypeScript packages
│       └── dcoder-sdk/    # Platform SDK
│
├── infrastructure/        # Infrastructure as code
│   ├── docker-compose.base.yml
│   ├── postgres/
│   ├── redis/
│   ├── observability/
│   └── ...
│
├── tools/                 # Build tools and scripts
│   ├── scripts/           # Helper scripts
│   ├── docker/            # Docker utilities
│   └── ci/                # CI/CD scripts
│
├── docs/                  # Documentation
├── .github/               # GitHub workflows & CODEOWNERS
├── nx.json                # Nx workspace config
├── package.json           # Root package.json
├── pnpm-workspace.yaml    # pnpm workspace
├── docker-compose.yml     # Root orchestrator
└── Makefile              # Developer commands
```

## 💻 Development

### Common Commands

```bash
# Infrastructure management
make infra-up              # Start infrastructure
make infra-down            # Stop infrastructure
make infra-logs            # View infrastructure logs

# Service management
make service-up SERVICE=platform-api    # Start specific service
make service-logs SERVICE=platform-api  # View service logs
make dev-up                            # Start full stack

# Development workflows
make build-all             # Build all services
make test-all              # Run all tests
make lint-all              # Lint all services

# Nx commands
pnpm nx graph              # View dependency graph
pnpm nx affected --target=test    # Test affected services
pnpm nx affected --target=build   # Build affected services

# Cleanup
make clean                 # Clean build artifacts
make reset                 # Full reset (WARNING: deletes data!)
```

### Working on a Service

```bash
# Option 1: Using make
make service-up SERVICE=platform-api

# Option 2: Direct docker-compose
cd services/platform-api
docker-compose up

# Option 3: Full stack
docker-compose --profile full up -d
```

### Creating a Changeset

```bash
pnpm changeset
```

## 🧪 Testing

```bash
# Test specific service
pnpm nx test platform-api

# Test all affected by changes
pnpm nx affected --target=test

# Test everything
make test-all
```

## 📊 Monitoring & Observability

- **Grafana**: http://localhost:3005 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Temporal UI**: http://localhost:8088
- **MinIO Console**: http://localhost:9001

## 🔐 Security

### Deloitte IP Protection

- System prompts encrypted using envelope encryption (AES-GCM)
- Runtime-only decryption
- Complete audit trails with cryptographic signatures
- Master control for access revocation

### Authentication

- SSO/OIDC integration via Logto
- ABAC (Attribute-Based Access Control) with Casbin
- Multi-tenancy at org/group/user levels
- Feature flags and quota enforcement

## 📖 Documentation

- [Contributing Guide](CONTRIBUTING.md)
- [Architecture Overview](docs/project-docs/releases/R1/ARCHITECTURE.md)
- [Service Contracts](docs/project-docs/releases/R1/SERVICE_CONTRACTS.md)
- [Monorepo Workflow](docs/runbooks/monorepo-workflow.md)

## 🛠️ Technology Stack

- **Gateways**: Kong 3.8 OSS, LiteLLM Proxy
- **Backend**: FastAPI (Python)
- **Orchestration**: Temporal, NATS JetStream
- **LLM Ops**: Agenta, MLFlow, Langfuse
- **RAG**: LlamaIndex, pgvector (MVP) → Milvus (scale)
- **UI**: Open WebUI, Next.js
- **Observability**: Prometheus, Grafana, Loki, OpenTelemetry
- **Auth**: Logto / Keycloak
- **Build**: Nx, pnpm workspaces

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

PROPRIETARY - Deloitte USI IGS. All rights reserved.

## 🔗 Links

- [GitHub Issues](https://github.com/deloitte/dcoder-platform/issues)
- [Slack Channel](#dcoder-platform)
- [Documentation](docs/)

---

**Built with ❤️ by Deloitte USI IGS**

