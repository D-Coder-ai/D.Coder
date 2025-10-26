#!/bin/bash
# View logs for specific service

if [ -z "$1" ]; then
    echo "Usage: $0 <service-name>"
    echo "Example: $0 platform-api"
    echo ""
    echo "Available services:"
    docker-compose ps --services
    exit 1
fi

docker-compose logs -f "$1"

