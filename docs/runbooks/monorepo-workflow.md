# Monorepo Workflow Guide

This guide explains how to work effectively in the D.Coder monorepo.

## Table of Contents

- [Understanding the Monorepo](#understanding-the-monorepo)
- [Daily Workflows](#daily-workflows)
- [Service Independence](#service-independence)
- [Versioning & Releases](#versioning--releases)
- [CI/CD Integration](#cicd-integration)
- [Best Practices](#best-practices)

## Understanding the Monorepo

D.Coder uses Nx for intelligent build orchestration:

- **Dependency Graph**: Nx understands relationships between services and packages
- **Affected Builds**: Only build/test what changed
- **Caching**: Build once, reuse everywhere
- **Task Pipeline**: Automatic task ordering based on dependencies

### Viewing the Dependency Graph

```bash
pnpm nx graph
```

This opens an interactive visualization showing how services and packages depend on each other.

## Daily Workflows

### 1. Starting Fresh

```bash
# Pull latest changes
git pull origin main

# Install dependencies
pnpm install

# Start infrastructure
make infra-up

# Start your service
make service-up SERVICE=platform-api
```

### 2. Working on a Feature

```bash
# Create feature branch
git checkout -b feat/add-quota-alerts

# Make changes to service
cd services/platform-api
# Edit files...

# Test your changes
pnpm nx test platform-api

# Test affected services (what might break)
pnpm nx affected --target=test

# Lint
pnpm nx lint platform-api
```

### 3. Creating a Changeset

For any user-facing change:

```bash
pnpm changeset
```

Answer prompts:
1. **Which packages changed?** Select `platform-api`
2. **What type of change?** Choose `minor` (feature) or `patch` (fix)
3. **Summary:** "Add quota alert notifications"

This creates a file in `.changeset/` that tracks your change.

### 4. Committing Changes

```bash
git add .
git commit -m "feat(platform-api): add quota alert notifications

- Implement Redis-based quota monitoring
- Add email notifications via SendGrid
- Update API documentation

Closes #123"

git push origin feat/add-quota-alerts
```

### 5. Creating a Pull Request

1. Push your branch
2. Open PR on GitHub
3. GitHub Actions will:
   - Detect affected services
   - Run tests only for affected services
   - Build Docker images (if Dockerfiles changed)
4. Request review from code owners (auto-assigned)

## Service Independence

### Key Principles

1. **Services can only depend on packages**, never other services
2. **Cross-service communication** happens via APIs/events
3. **Each service** has its own version
4. **Packages** are shared libraries used by multiple services

### Example: Adding a New Shared Model

```bash
# 1. Add model to shared package
cd packages/python/dcoder-common
# Edit dcoder_common/models/quota.py

# 2. Test the package
pnpm nx test dcoder-common

# 3. Build the package
pnpm nx build dcoder-common

# 4. Use in services
# Services automatically get the updated package via volume mounts in dev
# In production, Docker builds install the package
```

### Example: Service-to-Service Communication

**Bad** (direct import):
```python
# ❌ Don't do this
from services.platform_api.models import Tenant
```

**Good** (API call):
```python
# ✅ Do this
import httpx

async def get_tenant(tenant_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://platform-api:8082/v1/tenants/{tenant_id}")
        return response.json()
```

**Good** (shared package):
```python
# ✅ Do this
from dcoder_common.models import TenantContext
```

## Versioning & Releases

### Semantic Versioning

We follow [SemVer](https://semver.org/):

- **Major (1.0.0)**: Breaking changes
- **Minor (0.1.0)**: New features (backward compatible)
- **Patch (0.0.1)**: Bug fixes

### Changeset Workflow

1. **Development**: Create changeset with your PR
2. **Merge**: PR with changeset merges to `main`
3. **Version PR**: Changeset bot creates "Version Packages" PR
4. **Release**: Merging Version PR releases packages

### Example Changeset

After running `pnpm changeset`:

```md
---
"@dcoder/platform-api": minor
---

Add quota alert notifications

Implement Redis-based quota monitoring with email alerts
```

### Independent Versioning

Services can be at different versions:

```
@dcoder/platform-api: 2.3.1
@dcoder/agent-orchestrator: 1.5.0
@dcoder/knowledge-rag: 1.0.2
```

This allows:
- Faster releases for actively developed services
- Stable versions for mature services
- Independent deployment schedules

## CI/CD Integration

### Path-Filtered Workflows

GitHub Actions only run for changed code:

```yaml
on:
  pull_request:
    paths:
      - 'services/**'      # Only trigger if services changed
      - 'packages/**'      # Or if packages changed
```

### Affected Builds

CI uses `nx affected` to build only what changed:

```bash
# In CI
pnpm nx affected --target=test --base=origin/main
```

### Docker Image Builds

Only services with changed Dockerfiles get rebuilt:

```yaml
# CI detects changed Dockerfiles
services/platform-api/Dockerfile changed
→ Build & push dcoder/platform-api:sha-abc123
```

### Build Matrix

CI tests affected services in parallel:

```yaml
strategy:
  matrix:
    service: [platform-api, agent-orchestrator]  # Detected automatically

steps:
  - name: Test ${{ matrix.service }}
    run: pnpm nx test ${{ matrix.service }}
```

## Best Practices

### 1. Run Affected Commands

Instead of:
```bash
pnpm nx run-many --target=test --all  # Tests everything
```

Do:
```bash
pnpm nx affected --target=test  # Tests only what changed
```

### 2. Use the Dependency Graph

Before making cross-package changes:

```bash
pnpm nx graph
```

Understand what might be affected by your change.

### 3. Keep Services Decoupled

- Don't import from other services
- Use shared packages for common code
- Communicate via APIs/events

### 4. Test Locally with Affected

```bash
# See what will run in CI
pnpm nx affected --target=test --base=origin/main

# Run the same tests locally
pnpm nx affected --target=test
```

### 5. Clean Changesets

Good:
```md
---
"@dcoder/platform-api": minor
---

Add quota alert notifications

- Redis-based monitoring
- Email alerts via SendGrid
- Updated API docs
```

Bad:
```md
---
"@dcoder/platform-api": minor
---

stuff
```

### 6. Service README Files

Each service should have a README explaining:
- Purpose
- API endpoints
- Configuration
- Development setup
- Testing

### 7. Docker Development

Services run in Docker with volume mounts:

```yaml
volumes:
  - ./services/platform-api/src:/app/src:ro  # Hot reload
  - ./packages/python:/app/packages/python:ro  # Shared packages
```

Changes to code are immediately reflected without rebuilding.

## Common Scenarios

### Adding a New Service

```bash
# 1. Create service directory
mkdir -p services/my-service

# 2. Add project.json
cat > services/my-service/project.json << EOF
{
  "name": "my-service",
  "projectType": "application",
  "targets": {
    "build": {...},
    "test": {...}
  }
}
EOF

# 3. Add package.json
# 4. Add Dockerfile
# 5. Add to docker-compose.yml
# 6. Create changeset
pnpm changeset
```

### Adding a New Package

```bash
# 1. Create package directory
mkdir -p packages/python/my-package

# 2. Add pyproject.toml
# 3. Add project.json
# 4. Add to pnpm-workspace.yaml
# 5. Install in services that need it
```

### Debugging CI Failures

```bash
# 1. See what CI tested
git diff origin/main...HEAD --name-only

# 2. Run the same tests locally
pnpm nx affected --target=test --base=origin/main

# 3. Check specific service
pnpm nx test platform-api

# 4. View dependency graph
pnpm nx graph
```

## Troubleshooting

### "No affected projects"

Your changes don't affect any Nx projects. This can happen if:
- You only changed documentation
- Changes are in non-tracked directories
- You need to run `pnpm install` after pulling

### "Build cache miss"

Nx caching is working correctly:
- First build: cache miss (builds from scratch)
- Second build: cache hit (instant)

To clear cache:
```bash
pnpm nx reset
```

### "Circular dependency detected"

You've created a dependency cycle. Check the graph:
```bash
pnpm nx graph
```

Remove the circular dependency.

## Further Reading

- [Nx Documentation](https://nx.dev)
- [Changesets Documentation](https://github.com/changesets/changesets)
- [Monorepo Best Practices](https://monorepo.tools/)
- [Contributing Guide](../../CONTRIBUTING.md)

