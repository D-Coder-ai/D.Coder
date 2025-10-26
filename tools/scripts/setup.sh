#!/bin/bash

# Main setup script for D.Coder platform
# This script orchestrates the complete setup process

echo "======================================"
echo "   D.Coder Platform Setup Script     "
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# Step 1: Clone repositories
echo -e "${CYAN}Step 1: Cloning repositories...${NC}"
./scripts/clone-repos.sh
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to clone repositories${NC}"
    exit 1
fi
echo ""

# Step 2: Initialize development environment
echo -e "${CYAN}Step 2: Initializing development environment...${NC}"
./scripts/init-dev.sh
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to initialize development environment${NC}"
    exit 1
fi
echo ""

# Step 3: Setup Python virtual environments
echo -e "${CYAN}Step 3: Setting up Python environments for services...${NC}"

PYTHON_SERVICES=(
    "platform-api"
    "llmops"
    "agent-orchestrator"
    "knowledge-rag"
    "integrations"
)

for service in "${PYTHON_SERVICES[@]}"; do
    if [ -d "../${service}" ]; then
        echo -e "${BLUE}Setting up ${service}...${NC}"
        cd "../${service}"

        # Create virtual environment
        python -m venv venv

        # Create basic requirements.txt if it doesn't exist
        if [ ! -f requirements.txt ]; then
            cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
sqlalchemy==2.0.23
alembic==1.12.1
redis==5.0.1
httpx==0.25.2
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
EOF
            echo -e "${GREEN}✓ Created requirements.txt for ${service}${NC}"
        fi

        cd - > /dev/null
    fi
done
echo ""

# Step 4: Setup Node.js environments
echo -e "${CYAN}Step 4: Setting up Node.js environment for client apps...${NC}"

if [ -d "../client-apps" ]; then
    cd "../client-apps"

    # Create package.json if it doesn't exist
    if [ ! -f package.json ]; then
        cat > package.json << EOF
{
  "name": "dcoder-client-apps",
  "version": "1.0.0",
  "description": "D.Coder Client Applications",
  "private": true,
  "workspaces": [
    "admin-dashboard",
    "deloitte-dashboard"
  ],
  "scripts": {
    "dev": "npm run dev --workspaces",
    "build": "npm run build --workspaces",
    "test": "npm run test --workspaces"
  },
  "devDependencies": {
    "concurrently": "^8.2.2"
  }
}
EOF
        echo -e "${GREEN}✓ Created package.json for client-apps${NC}"
    fi

    cd - > /dev/null
fi
echo ""

# Step 5: Create git hooks
echo -e "${CYAN}Step 5: Setting up git hooks...${NC}"

# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for D.Coder platform

# Run linters for Python files
if git diff --cached --name-only | grep -q "\.py$"; then
    echo "Running Python linters..."
    # Add your Python linting commands here
fi

# Run linters for TypeScript/JavaScript files
if git diff --cached --name-only | grep -q "\.[jt]sx\?$"; then
    echo "Running TypeScript/JavaScript linters..."
    # Add your JS/TS linting commands here
fi
EOF

chmod +x .git/hooks/pre-commit
echo -e "${GREEN}✓ Git hooks configured${NC}"
echo ""

# Step 6: Generate documentation
echo -e "${CYAN}Step 6: Generating initial documentation...${NC}"

# Create main README if it doesn't exist
if [ ! -f README.md ]; then
    cat > README.md << 'EOF'
# D.Coder LLM Platform

Enterprise-grade, AI-native infrastructure for building and deploying Large Language Model applications.

## 🚀 Quick Start

1. **Prerequisites**
   - Docker & Docker Compose
   - Python 3.11+
   - Node.js 18+
   - Tilt (optional, for hot-reload development)

2. **Setup**
   ```bash
   ./scripts/setup.sh
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start Services**
   ```bash
   # Start all infrastructure
   docker-compose up -d

   # Or use Tilt for development
   tilt up
   ```

## 📁 Repository Structure

- `platform/` - Main orchestration and deployment
- `platform/gateways/kong/` - Kong platform gateway
- `platform-api/` - Core platform API
- `llmops/` - LLMOps platform
- `agent-orchestrator/` - Agent orchestration service
- `knowledge-rag/` - Knowledge & RAG service
- `integrations/` - External integrations
- `client-apps/` - Web applications
- `shared/` - Shared libraries

## 📖 Documentation

- [Platform Architecture](docs/PLATFORM_ARCHITECTURE.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [API Documentation](docs/API.md)

## 🛠️ Development

See individual service README files for service-specific development instructions.

## 📝 License

Proprietary - D.Coder AI
EOF
    echo -e "${GREEN}✓ Created README.md${NC}"
fi

# Final summary
echo ""
echo -e "${GREEN}======================================"
echo "   ✨ Setup Complete!"
echo "======================================${NC}"
echo ""
echo "📋 Summary:"
echo "  ✅ Repositories cloned"
echo "  ✅ Development environment initialized"
echo "  ✅ Python environments prepared"
echo "  ✅ Node.js environment prepared"
echo "  ✅ Git hooks configured"
echo "  ✅ Documentation generated"
echo ""
echo "🚀 Next Steps:"
echo "  1. Configure your .env file"
echo "  2. Start services: docker-compose up -d"
echo "  3. Begin development in service directories"
echo ""
echo "📚 Useful Commands:"
echo "  tilt up              - Start development with hot-reload"
echo "  docker-compose up    - Start all services"
echo "  docker-compose logs  - View service logs"
echo "  ./scripts/update-repos.sh - Update all repositories"
echo ""
echo "Happy coding! 🎉"