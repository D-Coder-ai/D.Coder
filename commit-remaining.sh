#!/bin/bash

# Commit and push remaining repositories

echo "Committing and pushing remaining repositories..."

# LLMOps
cd llmops
git add -A
git commit -m "Initial setup: LLMOps Platform Service

- Basic FastAPI structure
- Docker configuration for Agenta, MLFlow, Langfuse integration
- Directory structure following hexagonal architecture"
git push origin main
cd ..

# Agent Orchestrator
cd agent-orchestrator
git add -A
git commit -m "Initial setup: Agent Orchestration Service

- Basic FastAPI structure
- Docker configuration for Temporal and LangGraph integration
- Directory structure following hexagonal architecture"
git push origin main
cd ..

# Knowledge RAG
cd knowledge-rag
git add -A
git commit -m "Initial setup: Knowledge & RAG Service

- Basic FastAPI structure
- Docker configuration for pgvector and LlamaIndex
- Directory structure following hexagonal architecture"
git push origin main
cd ..

# Integrations
cd integrations
git add -A
git commit -m "Initial setup: Integrations Service

- Basic FastAPI structure
- Docker configuration for external connectors
- Directory structure following hexagonal architecture"
git push origin main
cd ..

# Client Apps
cd client-apps
git add -A
git commit -m "Initial setup: Client Applications

- Node.js configuration
- Docker setup for Open WebUI and dashboards
- Package.json for workspace management"
git push origin main
cd ..

# Shared
cd shared
git add -A
git commit -m "Initial setup: Shared Libraries

- Python common utilities structure
- TypeScript component library structure
- Setup.py for Python packages"
git push origin main
cd ..

echo "✅ All repositories have been committed and pushed!"