# D.Coder Platform Infrastructure

This directory contains the base infrastructure services required by all D.Coder platform services.

## Overview

The `docker-compose.base.yml` file defines the core infrastructure layer that provides:
- **Data Persistence**: PostgreSQL, Redis, MinIO
- **Event Streaming**: NATS JetStream
- **Workflow Orchestration**: Temporal + Temporal UI

This infrastructure layer is designed to run independently and be shared across all platform services.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Platform Services Layer                    │
│  (Kong, LiteLLM, Platform API, Agent Orchestrator, etc) │
└─────────────────────────────────────────────────────────┘
                         ↓ depends on
┌─────────────────────────────────────────────────────────┐
│           Base Infrastructure Layer (this)              │
│  PostgreSQL │ Redis │ MinIO │ NATS │ Temporal          │
└─────────────────────────────────────────────────────────┘
```

## Services

### 1. PostgreSQL (Port 5432)
**Purpose**: Primary relational database

**Features**:
- PostgreSQL 16.2 with Alpine Linux
- pgvector extension for embeddings (MVP)
- Optimized for LLM workloads (200 max connections)
- Pre-configured databases for all platform services
- Database-per-tenant isolation strategy (R1)

**Health Check**: `pg_isready` with 10s interval

**Environment Variables**:
- `POSTGRES_USER` (default: dcoder)
- `POSTGRES_PASSWORD` (default: changeme)
- `POSTGRES_DB` (default: dcoder_platform)

**Databases Created**:
- `dcoder_platform` - Main platform database
- `temporal` - Temporal workflow database
- `temporal_visibility` - Temporal visibility database
- `litellm` - LiteLLM virtual keys
- `logto` - Authentication (if using Logto)
- `flagsmith` - Feature flags (if using Flagsmith)
- `platform_api`, `agent_orchestrator`, `knowledge_rag`, `integrations`, `llmops` - Service databases

### 2. Redis (Port 6379)
**Purpose**: Caching, session storage, rate limiting, LLM semantic cache

**Features**:
- Redis 7.2.4 with Alpine Linux
- AOF persistence enabled
- 2GB memory limit with LRU eviction
- Optimized for high-performance caching

**Health Check**: `redis-cli ping` with 10s interval

**Configuration**: `./redis/redis.conf`

### 3. MinIO (Ports 9000, 9001)
**Purpose**: S3-compatible object storage

**Features**:
- MinIO stable release (2024-03-15)
- Document storage for RAG
- Model artifacts for MLFlow
- Backup archives
- Prometheus metrics enabled

**Ports**:
- 9000: S3 API
- 9001: Web Console

**Health Check**: `mc ready local` with 30s interval

**Environment Variables**:
- `MINIO_ROOT_USER` (default: minioadmin)
- `MINIO_ROOT_PASSWORD` (default: minioadmin)

### 4. NATS JetStream (Ports 4222, 8222, 6222)
**Purpose**: Event streaming and pub/sub messaging

**Features**:
- NATS 2.10.12 with Alpine Linux
- JetStream enabled for durable streaming
- 1GB memory store, 10GB file store
- Cross-service event communication

**Ports**:
- 4222: Client connections
- 8222: HTTP monitoring
- 6222: Cluster port

**Health Check**: HTTP endpoint at `/healthz` with 10s interval

**Configuration**: `./nats/nats.conf`

### 5. Temporal (Port 7233)
**Purpose**: Durable workflow orchestration for AI agents

**Features**:
- Temporal 1.24.2 auto-setup
- PostgreSQL backend
- Durable agent execution
- Automatic retry and recovery
- Long-running workflow support

**Ports**:
- 7233: gRPC API
- 7234: Membership port
- 7235: History service
- 7239: Worker service

**Health Check**: `tctl cluster health` with 30s interval

**Dependencies**: Requires PostgreSQL to be healthy

### 6. Temporal UI (Port 8088)
**Purpose**: Web interface for monitoring Temporal workflows

**Features**:
- Temporal UI 2.25.0
- Workflow visualization
- Real-time monitoring
- Debugging capabilities

**Port**: 8088 (maps to internal 8080)

**Health Check**: HTTP endpoint with 30s interval

**Dependencies**: Requires Temporal to be healthy

## Quick Start

### 1. Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available for Docker
- Ports 5432, 6379, 4222, 7233, 8088, 9000, 9001 available

### 2. Environment Setup
Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and set your credentials:
```bash
# PostgreSQL
POSTGRES_USER=dcoder
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=dcoder_platform

# MinIO
MINIO_ROOT_USER=your_minio_user
MINIO_ROOT_PASSWORD=your_secure_password_here
```

### 3. Start Infrastructure
```bash
# From repository root
make infra-up

# Or directly from infrastructure directory
cd infrastructure
docker-compose -f docker-compose.base.yml up -d
```

### 4. Verify Services
Check that all services are healthy:
```bash
# From repository root
make status

# Or check individual services
docker ps --filter "name=dcoder-*"
docker-compose -f infrastructure/docker-compose.base.yml ps
```

### 5. Access Services
- **PostgreSQL**: `postgresql://dcoder:changeme@localhost:5432/dcoder_platform`
- **Redis**: `redis://localhost:6379`
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)
- **MinIO API**: http://localhost:9000
- **NATS Monitoring**: http://localhost:8222
- **Temporal UI**: http://localhost:8088

## Common Operations

### View Logs
```bash
# All services
make infra-logs

# Specific service
docker-compose -f infrastructure/docker-compose.base.yml logs -f postgres
docker logs dcoder-postgres -f
```

### Stop Infrastructure
```bash
# From repository root
make infra-down

# Or directly
docker-compose -f infrastructure/docker-compose.base.yml down
```

### Restart a Service
```bash
docker-compose -f infrastructure/docker-compose.base.yml restart postgres
```

### Check Health Status
```bash
# All services
docker-compose -f infrastructure/docker-compose.base.yml ps

# PostgreSQL
docker exec dcoder-postgres pg_isready -U dcoder

# Redis
docker exec dcoder-redis redis-cli ping

# NATS
curl http://localhost:8222/healthz

# Temporal
docker exec dcoder-temporal tctl cluster health
```

## Data Persistence

All data is stored in named Docker volumes:

```bash
# List volumes
docker volume ls | grep dcoder

# Volumes created:
# - dcoder-postgres-data
# - dcoder-redis-data
# - dcoder-minio-data
# - dcoder-nats-data
# - dcoder-temporal-data
```

### Backup Data
```bash
# PostgreSQL
docker exec dcoder-postgres pg_dump -U dcoder dcoder_platform > backup.sql

# Redis
docker exec dcoder-redis redis-cli --rdb /data/dump.rdb

# MinIO - use mc (MinIO Client)
# Install mc: https://min.io/docs/minio/linux/reference/minio-mc.html
```

### Reset Infrastructure
**WARNING**: This will delete ALL data!

```bash
# From repository root
make reset

# Or manually
docker-compose -f infrastructure/docker-compose.base.yml down -v
```

## Configuration Files

```
infrastructure/
├── docker-compose.base.yml          # Main infrastructure definition
├── docker-compose.dev.yml           # Development overrides
├── README.md                        # This file
├── nats/
│   └── nats.conf                    # NATS JetStream configuration
├── redis/
│   └── redis.conf                   # Redis configuration
└── volumes/
    └── postgres/
        └── init/
            └── 01-init-databases.sql  # Database initialization script
```

## Troubleshooting

### PostgreSQL Connection Refused
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check logs
docker logs dcoder-postgres

# Verify health
docker exec dcoder-postgres pg_isready -U dcoder
```

### Redis Connection Issues
```bash
# Check Redis logs
docker logs dcoder-redis

# Test connection
docker exec dcoder-redis redis-cli ping
```

### MinIO Not Accessible
```bash
# Check MinIO logs
docker logs dcoder-minio

# Verify ports
netstat -an | grep 9000
netstat -an | grep 9001
```

### Temporal Not Starting
```bash
# Check Temporal logs
docker logs dcoder-temporal

# Verify PostgreSQL is healthy
docker-compose -f infrastructure/docker-compose.base.yml ps postgres

# Check Temporal cluster health
docker exec dcoder-temporal tctl cluster health
```

### NATS JetStream Issues
```bash
# Check NATS logs
docker logs dcoder-nats

# Check JetStream status
curl http://localhost:8222/jsz
```

### Port Conflicts
If you get port binding errors:
```bash
# Check what's using the port (example for port 5432)
netstat -ano | findstr :5432  # Windows
lsof -i :5432                  # macOS/Linux

# Change port in docker-compose.base.yml if needed
# e.g., "5433:5432" to expose on host port 5433
```

## Performance Tuning

### PostgreSQL
The configuration includes optimized settings for LLM workloads:
- 200 max connections
- 256MB shared buffers
- 1GB effective cache size
- Optimized for SSD storage (random_page_cost=1.1)

To adjust for your hardware, edit the `command` section in `docker-compose.base.yml`.

### Redis
Redis is configured with:
- 2GB max memory
- LRU eviction policy
- AOF persistence with fsync every second

To adjust, edit `./redis/redis.conf`.

### NATS JetStream
JetStream is configured with:
- 1GB memory store
- 10GB file store

To adjust, edit `./nats/nats.conf`.

## Network

All services run on a custom bridge network named `dcoder-network`. This allows:
- Service discovery by container name
- Isolated network communication
- Easy integration with platform services

Platform services should connect to this network:
```yaml
networks:
  dcoder-network:
    external: true
```

## Security Notes

**Default Credentials (Change These!)**:
- PostgreSQL: dcoder/changeme
- MinIO: minioadmin/minioadmin
- Redis: No password (add one in production!)

**Production Recommendations**:
1. Use strong passwords for all services
2. Enable TLS/SSL for all connections
3. Use Docker secrets for sensitive data
4. Restrict network access with firewall rules
5. Enable Redis authentication (requirepass)
6. Use read-only file mounts where possible
7. Regular security updates for all images
8. Monitor and audit all access logs

## Next Steps

After infrastructure is running:
1. Start platform services (Kong, LiteLLM, Platform API)
2. Configure authentication (Logto)
3. Set up feature flags (Flagsmith)
4. Deploy application services
5. Configure observability stack

See the main project documentation in `docs/project-docs/releases/R1/` for complete setup instructions.
