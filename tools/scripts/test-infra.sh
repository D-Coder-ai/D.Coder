#!/bin/bash
set -e

echo "=== Testing Infrastructure ==="

echo "Postgres..."
docker-compose exec -T postgres pg_isready -U ${POSTGRES_USER:-dcoder}

echo "Redis AOF..."
docker-compose exec -T redis redis-cli info persistence | grep aof_enabled:yes

echo "NATS JetStream..."
curl -sf http://localhost:8222/varz | grep -q jetstream

echo "Prometheus targets..."
curl -sf http://localhost:9090/api/v1/targets | grep -q kong

echo "=== All tests passed ==="
