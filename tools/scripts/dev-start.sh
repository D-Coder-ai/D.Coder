#!/bin/bash
# Development startup script for D.Coder platform

set -e

echo "🚀 Starting D.Coder Platform Development Environment"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found"
    echo "📝 Creating .env from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ .env created. Please fill in your API keys before continuing."
        exit 1
    else
        echo "❌ .env.example not found. Cannot create .env file."
        exit 1
    fi
fi

# Check if pnpm is installed
if ! command -v pnpm &> /dev/null; then
    echo "❌ pnpm not found. Installing pnpm..."
    npm install -g pnpm
fi

# Install dependencies
echo "📦 Installing dependencies..."
pnpm install

# Start infrastructure
echo "🏗️  Starting infrastructure services..."
docker-compose -f infrastructure/docker-compose.base.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for infrastructure to be ready..."
sleep 5

# Check health
echo "🔍 Checking service health..."
docker-compose -f infrastructure/docker-compose.base.yml ps

echo ""
echo "✅ Infrastructure is running!"
echo ""
echo "📊 Available Services:"
echo "  - PostgreSQL:      localhost:5432"
echo "  - Redis:           localhost:6379"
echo "  - MinIO:           localhost:9000 (console: 9001)"
echo "  - NATS:            localhost:4222"
echo "  - Prometheus:      localhost:9090"
echo "  - Grafana:         localhost:3005 (admin/admin)"
echo "  - Temporal UI:     localhost:8088"
echo ""
echo "🎯 Next steps:"
echo "  1. Start services: make service-up SERVICE=platform-api"
echo "  2. Or full stack:  docker-compose --profile full up -d"
echo "  3. View logs:      make infra-logs"
echo ""

