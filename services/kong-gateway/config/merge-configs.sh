#!/bin/sh
# Merge Kong declarative config files for DB-less mode
# Combines LLM routes, platform routes, and health routes into single config

set -e

MERGED_CONFIG="/tmp/kong-merged.yaml"

echo "Merging Kong declarative configs..."

# Start with the base LLM config
cat /etc/kong/custom/kong.yml > ${MERGED_CONFIG}

# Merge platform services (append services and maintain format)
echo "" >> ${MERGED_CONFIG}
echo "# Platform Services Configuration" >> ${MERGED_CONFIG}
tail -n +2 /etc/kong/custom/routes/platform-services.yml | grep -v "^_format_version:" >> ${MERGED_CONFIG}

# Merge health routes
echo "" >> ${MERGED_CONFIG}
echo "# Health Check Routes" >> ${MERGED_CONFIG}
tail -n +2 /etc/kong/custom/routes/health.yml | grep -v "^_format_version:" | grep -v "^plugins:" >> ${MERGED_CONFIG}

echo "Config merge complete. Starting Kong..."
export KONG_DECLARATIVE_CONFIG=${MERGED_CONFIG}

# Use Kong's Docker entrypoint to start properly
exec /docker-entrypoint.sh kong docker-start

