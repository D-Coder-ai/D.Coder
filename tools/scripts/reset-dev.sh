#!/bin/bash
# Reset development environment (WARNING: Deletes all data!)

set -e

echo "⚠️  WARNING: This will delete ALL data in Docker volumes!"
echo "This includes databases, caches, and uploaded files."
echo ""
read -p "Are you sure you want to continue? (yes/no): " -r
echo

if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
    echo "Aborted."
    exit 1
fi

echo "🛑 Stopping all services..."
docker-compose down -v
docker-compose -f infrastructure/docker-compose.base.yml down -v

echo "🧹 Cleaning build artifacts..."
pnpm nx reset

echo "📁 Cleaning Python caches..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

echo "✅ Development environment reset complete!"
echo ""
echo "To start fresh:"
echo "  ./tools/scripts/dev-start.sh"

