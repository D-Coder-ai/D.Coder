#!/bin/bash

# Update all D.Coder service repositories to latest
# This script pulls the latest changes from all repositories

echo "🔄 Updating all D.Coder service repositories..."

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

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
FAILED_REPOS=()
UPDATED_REPOS=()
SKIPPED_REPOS=()

# Update each repository
for repo in "${REPOS[@]}"; do
    if [ -d "../${repo}" ]; then
        echo -e "${YELLOW}📥 Updating ${repo}...${NC}"

        cd "../${repo}"

        # Check if there are uncommitted changes
        if ! git diff-index --quiet HEAD -- 2>/dev/null; then
            echo -e "${YELLOW}⚠️  ${repo} has uncommitted changes, skipping...${NC}"
            SKIPPED_REPOS+=("${repo}")
        else
            # Fetch and pull latest changes
            git fetch origin
            git pull origin main

            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ Successfully updated ${repo}${NC}"
                UPDATED_REPOS+=("${repo}")
            else
                echo -e "${RED}❌ Failed to update ${repo}${NC}"
                FAILED_REPOS+=("${repo}")
            fi
        fi

        cd - > /dev/null
    else
        echo -e "${RED}❌ ${repo} directory not found${NC}"
        FAILED_REPOS+=("${repo}")
    fi
    echo ""
done

# Summary
echo "======================================="
echo "📊 Update Summary:"
echo "======================================="

if [ ${#UPDATED_REPOS[@]} -gt 0 ]; then
    echo -e "${GREEN}✅ Successfully updated (${#UPDATED_REPOS[@]}):${NC}"
    for repo in "${UPDATED_REPOS[@]}"; do
        echo "   - ${repo}"
    done
fi

if [ ${#SKIPPED_REPOS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Skipped due to uncommitted changes (${#SKIPPED_REPOS[@]}):${NC}"
    for repo in "${SKIPPED_REPOS[@]}"; do
        echo "   - ${repo}"
    done
fi

if [ ${#FAILED_REPOS[@]} -gt 0 ]; then
    echo -e "${RED}❌ Failed to update (${#FAILED_REPOS[@]}):${NC}"
    for repo in "${FAILED_REPOS[@]}"; do
        echo "   - ${repo}"
    done
    exit 1
fi

echo ""
echo "✨ Update complete!"