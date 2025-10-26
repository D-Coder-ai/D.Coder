#!/bin/bash
# Detect affected services for CI/CD

set -e

BASE_REF=${1:-"origin/main"}

echo "Detecting services affected since $BASE_REF..."

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    pnpm install --frozen-lockfile
fi

# Get affected services
AFFECTED=$(pnpm nx show projects --affected --base=$BASE_REF --type=app)

if [ -z "$AFFECTED" ]; then
    echo "No affected services"
    echo "[]"
else
    echo "Affected services:"
    echo "$AFFECTED"
    
    # Convert to JSON array for GitHub Actions
    echo "$AFFECTED" | jq -R -s -c 'split("\n") | map(select(length > 0))'
fi

