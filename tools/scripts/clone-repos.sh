#!/bin/bash

# Clone all D.Coder service repositories
# This script should be run from the parent directory containing all repos

echo "🚀 Cloning all D.Coder service repositories..."

# GitHub organization
ORG="D-Coder-ai"
BASE_URL="https://github.com/${ORG}"

# List of repositories
REPOS=(
    "platform"
    "gateway"
    "platform-api"
    "llmops"
    "agent-orchestrator"
    "knowledge-rag"
    "integrations"
    "client-apps"
    "shared"
)

# Clone each repository
for repo in "${REPOS[@]}"; do
    if [ -d "../${repo}" ]; then
        echo "✓ ${repo} already exists, skipping..."
    else
        echo "📥 Cloning ${repo}..."
        git clone "${BASE_URL}/${repo}.git" "../${repo}"
        if [ $? -eq 0 ]; then
            echo "✅ Successfully cloned ${repo}"
        else
            echo "❌ Failed to clone ${repo}"
            exit 1
        fi
    fi
done

echo "✨ All repositories cloned successfully!"
echo ""
echo "📁 Repository structure:"
ls -la ../ | grep "^d" | grep -E "(platform|gateway|platform-api|llmops|agent-orchestrator|knowledge-rag|integrations|client-apps|shared)"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and configure"
echo "2. Run ./scripts/setup.sh to initialize development environment"
echo "3. Run 'tilt up' to start development with hot-reload"