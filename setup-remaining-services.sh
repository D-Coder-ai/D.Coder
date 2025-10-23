#!/bin/bash

# Script to set up basic structure for remaining services

echo "Setting up remaining D.Coder services..."

# Function to create basic Python service structure
setup_python_service() {
    local service_name=$1
    local service_desc=$2
    local port=$3

    echo "Setting up $service_name..."

    cd "$service_name" || return

    # Create directory structure
    mkdir -p src/{domain,application,adapters/{inbound,outbound},infrastructure}
    mkdir -p tests/{unit,integration,e2e}

    # Create Dockerfile
    cat > Dockerfile << EOF
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc postgresql-client && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE $port
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "$port"]
EOF

    # Create requirements.txt
    cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
sqlalchemy==2.0.23
redis==5.0.1
httpx==0.25.2
prometheus-client==0.19.0
EOF

    # Create docker-compose.yml
    cat > docker-compose.yml << EOF
version: '3.8'

services:
  $service_name:
    build: .
    ports:
      - "$port:$port"
    environment:
      SERVICE_NAME: $service_name
      SERVICE_PORT: $port
      DEBUG: "true"
    volumes:
      - ./src:/app/src
EOF

    # Create basic main.py
    cat > src/main.py << EOF
"""
$service_desc
"""

from fastapi import FastAPI

app = FastAPI(
    title="$service_name",
    description="$service_desc",
    version="1.0.0"
)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "$service_name"}
EOF

    cd ..
}

# Set up each service
setup_python_service "llmops" "LLMOps Platform Service - Prompt engineering, experimentation, evaluation" 8081
setup_python_service "agent-orchestrator" "Agent Orchestration Service - Durable workflows with Temporal and LangGraph" 8083
setup_python_service "knowledge-rag" "Knowledge & RAG Service - Document processing and semantic search" 8084
setup_python_service "integrations" "Integrations Service - JIRA, Bitbucket, Confluence, SharePoint connectors" 8085

# Set up client-apps (Node.js)
echo "Setting up client-apps..."
cd client-apps || exit

cat > package.json << 'EOF'
{
  "name": "dcoder-client-apps",
  "version": "1.0.0",
  "description": "D.Coder Client Applications",
  "private": true,
  "scripts": {
    "dev": "echo 'Development mode'",
    "build": "echo 'Building apps'"
  }
}
EOF

cat > Dockerfile << 'EOF'
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
EXPOSE 3000 3001 3002
CMD ["npm", "run", "dev"]
EOF

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  client-apps:
    build: .
    ports:
      - "3000:3000"
      - "3001:3001"
      - "3002:3002"
    environment:
      NODE_ENV: development
    volumes:
      - .:/app
      - /app/node_modules
EOF

cd ..

# Set up shared repository
echo "Setting up shared repository..."
cd shared || exit

# Create Python shared library structure
mkdir -p python/{common/src/dcoder_common,models/src/dcoder_models}
mkdir -p typescript/{ui-components/src,api-client/src}

# Python common setup.py
cat > python/common/setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="dcoder-common",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pydantic>=2.0.0",
        "sqlalchemy>=2.0.0",
    ]
)
EOF

# TypeScript package.json
cat > typescript/ui-components/package.json << 'EOF'
{
  "name": "@dcoder/ui-components",
  "version": "1.0.0",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "dev": "tsc --watch"
  }
}
EOF

cd ..

echo "✅ All services have been set up with basic structure!"