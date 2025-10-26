#!/bin/bash

# Initialize development environment for D.Coder platform
# This script sets up the local development environment

echo "🚀 Initializing D.Coder development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker from https://docker.com"
    exit 1
fi
echo -e "${GREEN}✓ Docker found${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose found${NC}"

# Check Tilt (optional but recommended)
if command -v tilt &> /dev/null; then
    echo -e "${GREEN}✓ Tilt found${NC}"
else
    echo -e "${YELLOW}⚠️  Tilt not found (optional but recommended for hot-reload)${NC}"
    echo "Install from: https://docs.tilt.dev/install.html"
fi

# Check gh CLI
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}⚠️  GitHub CLI not found${NC}"
    echo "Install from: https://cli.github.com/"
fi

# Setup environment file
echo -e "${BLUE}🔧 Setting up environment configuration...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file from template${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env file with your configuration${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Create necessary directories
echo -e "${BLUE}📁 Creating necessary directories...${NC}"
mkdir -p infra/volumes/{postgres/init,redis}
mkdir -p infra/kong/plugins
mkdir -p infra/observability/{prometheus,grafana/{dashboards,datasources},loki}
echo -e "${GREEN}✓ Directories created${NC}"

# Create basic configuration files
echo -e "${BLUE}📝 Creating configuration files...${NC}"

# Create Kong configuration
cat > infra/kong/kong.yml << 'EOF'
_format_version: "3.0"
services:
  - name: health-check
    url: http://httpbin.org/status/200
    routes:
      - name: health-route
        paths:
          - /health
EOF
echo -e "${GREEN}✓ Created Kong configuration${NC}"

# Create Prometheus configuration
cat > infra/observability/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'kong'
    static_configs:
      - targets: ['kong:8001']

  - job_name: 'platform-api'
    static_configs:
      - targets: ['platform-api:8082']
EOF
echo -e "${GREEN}✓ Created Prometheus configuration${NC}"

# Create Loki configuration
cat > infra/observability/loki/loki.yml << 'EOF'
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/boltdb-shipper-active
    cache_location: /loki/boltdb-shipper-cache
    shared_store: filesystem
  filesystem:
    directory: /loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h
EOF
echo -e "${GREEN}✓ Created Loki configuration${NC}"

# Create Grafana datasource
cat > infra/observability/grafana/datasources/datasources.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
EOF
echo -e "${GREEN}✓ Created Grafana datasources${NC}"

# Pull Docker images
echo -e "${BLUE}🐳 Pulling Docker images...${NC}"
docker-compose pull
echo -e "${GREEN}✓ Docker images pulled${NC}"

# Initialize databases
echo -e "${BLUE}🗄️ Initializing databases...${NC}"
docker-compose up -d postgres redis
sleep 5

# Run Kong migrations
echo -e "${BLUE}🔧 Running Kong migrations...${NC}"
docker-compose up kong-migrations
echo -e "${GREEN}✓ Kong migrations completed${NC}"

# Stop services
docker-compose down

echo ""
echo -e "${GREEN}✨ Development environment initialized successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run 'docker-compose up -d' to start all infrastructure services"
echo "3. Run 'tilt up' for hot-reload development (if Tilt is installed)"
echo "4. Or work on individual services in their respective directories"
echo ""
echo "Service URLs (when running):"
echo "  Kong Gateway:    http://localhost:8000"
echo "  Kong Admin:      http://localhost:8001"
echo "  Grafana:         http://localhost:3005 (admin/admin)"
echo "  Prometheus:      http://localhost:9090"
echo "  Temporal UI:     http://localhost:8088"
echo "  MinIO Console:   http://localhost:9001 (minioadmin/minioadmin)"
echo "  Logto:          http://localhost:3001"
echo "  Flagsmith:      http://localhost:8090"