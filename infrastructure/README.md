# D.Coder Platform Infrastructure

This directory contains the always-on foundation infrastructure for the D.Coder platform.

## Components

### Data Stores
- **PostgreSQL** (5432): Main relational database with pgvector extension
- **Redis** (6379): Caching, session storage, rate limiting
- **MinIO** (9000/9001): S3-compatible object storage

### Message Queue
- **NATS** (4222/8222): Event-driven messaging with JetStream

### Orchestration
- **Temporal** (7233): Durable workflow execution
- **Temporal UI** (8088): Workflow visualization and debugging

### Observability
- **Prometheus** (9090): Metrics collection
- **Grafana** (3005): Dashboards and visualization
- **Loki** (3100): Log aggregation

### Authentication & Features
- **Logto** (3001/3002): SSO and authentication
- **Flagsmith** (8090): Feature flags and toggles

## Usage

### Start Infrastructure
```bash
# From repo root
make infra-up

# Or directly
docker-compose -f infrastructure/docker-compose.base.yml up -d
```

### Stop Infrastructure
```bash
make infra-down
```

### View Logs
```bash
make infra-logs
```

## Configuration

Infrastructure services are configured through:
- Environment variables (`.env` file in repo root)
- Service-specific config files in subdirectories
- Docker Compose volume mounts

## Directory Structure

```
infrastructure/
├── docker-compose.base.yml    # Base infrastructure stack
├── docker-compose.dev.yml     # Development overrides
├── postgres/                  # PostgreSQL init scripts
├── redis/                     # Redis configuration
├── nats/                      # NATS configuration
├── observability/             # Prometheus, Grafana, Loki configs
├── auth/                      # Logto configs (future)
└── policies/                  # OPA policies
```

## Health Checks

All infrastructure services expose health check endpoints:
- PostgreSQL: `pg_isready`
- Redis: `redis-cli ping`
- NATS: `http://localhost:8222/healthz`
- Prometheus: `http://localhost:9090/-/healthy`
- Grafana: `http://localhost:3005/api/health`

## Persistence

Data persists in Docker volumes:
- `postgres-data`
- `redis-data`
- `minio-data`
- `nats-data`
- `prometheus-data`
- `grafana-data`
- `loki-data`

To reset all data:
```bash
make reset  # WARNING: Deletes all data!
```
