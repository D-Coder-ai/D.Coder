# Contributing to D.Coder Platform

Thank you for your interest in contributing to the D.Coder Platform! This document provides guidelines and workflows for contributors.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Monorepo Structure](#monorepo-structure)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Code Review](#code-review)

## Getting Started

### Prerequisites

- **Node.js** 20+ and **pnpm** 8+
- **Docker** and **Docker Compose**
- **Python** 3.11+
- **Git**

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/deloitte/dcoder-platform.git
   cd dcoder-platform
   ```

2. **Install dependencies**:
   ```bash
   make install
   # or
   pnpm install
   ```

3. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Start infrastructure**:
   ```bash
   make infra-up
   # or
   ./tools/scripts/dev-start.sh
   ```

## Development Workflow

### Working on a Service

1. **Start infrastructure** (if not already running):
   ```bash
   make infra-up
   ```

2. **Start your service**:
   ```bash
   make service-up SERVICE=platform-api
   # or
   cd services/platform-api
   docker-compose up
   ```

3. **Make changes** - code changes are hot-reloaded via volume mounts

4. **Run tests**:
   ```bash
   pnpm nx test platform-api
   ```

5. **Lint your code**:
   ```bash
   pnpm nx lint platform-api
   ```

### Working on Multiple Services

Use the root docker-compose with profiles:

```bash
# Start gateways + infrastructure
docker-compose --profile gateways up -d

# Start all services
docker-compose --profile full up -d
```

### Working on Shared Packages

Shared packages are in `packages/python/` and `packages/typescript/`:

```bash
# Work on Python package
cd packages/python/dcoder-common
poetry install
poetry run pytest

# Work on TypeScript package
cd packages/typescript/dcoder-sdk
pnpm install
pnpm test
```

## Monorepo Structure

Our repository follows a clear structure:

```
D.Coder/
├── services/          # All application services
├── packages/          # Shared libraries
├── infrastructure/    # Infrastructure configs
├── tools/            # Build scripts and utilities
└── docs/             # Documentation
```

### Service Boundaries

- **Services** can only depend on **packages**, never on other services
- Cross-service communication happens via APIs/events only
- Each service has its own version and can be released independently

## Making Changes

### Branch Naming

- `feat/description` - New features
- `fix/description` - Bug fixes
- `refactor/description` - Code refactoring
- `docs/description` - Documentation updates
- `chore/description` - Maintenance tasks

### Creating a Changeset

For any user-facing change (features, fixes, breaking changes):

```bash
pnpm changeset
```

Follow the prompts to:
1. Select which packages/services changed
2. Choose the version bump type (major, minor, patch)
3. Provide a summary

The changeset file will be committed with your PR.

### Code Style

- **Python**: Follow PEP 8, use `black` for formatting, `ruff` for linting
- **TypeScript**: Use Prettier for formatting, ESLint for linting
- **Commit messages**: Follow Conventional Commits format

## Testing

### Unit Tests

```bash
# Test a specific service
pnpm nx test platform-api

# Test all affected services
pnpm nx affected --target=test

# Test everything
make test-all
```

### Integration Tests

Integration tests run in Docker:

```bash
cd services/platform-api
docker-compose up -d
poetry run pytest tests/integration/
```

### E2E Tests

Full stack tests:

```bash
docker-compose --profile full up -d
# Run E2E tests
```

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Test updates
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

**Examples**:
```
feat(platform-api): add tenant quota enforcement

- Implement quota middleware
- Add usage tracking to Redis
- Update API documentation

Closes #123
```

## Pull Request Process

### Before Creating a PR

1. **Ensure tests pass**:
   ```bash
   pnpm nx affected --target=test
   pnpm nx affected --target=lint
   ```

2. **Create changeset** (if applicable):
   ```bash
   pnpm changeset
   ```

3. **Update documentation** if needed

4. **Commit with conventional format**

### Creating the PR

1. **Push your branch** to GitHub
2. **Create PR** from your branch to `main`
3. **Fill out PR template**:
   - Description of changes
   - Link to related issues
   - Screenshots (if UI changes)
   - Testing performed
   - Changeset included (yes/no)

4. **Request reviews** from code owners (auto-assigned)

### PR Checklist

- [ ] Tests added/updated and passing
- [ ] Linting passes
- [ ] Changeset created (if needed)
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Screenshots included (if UI)

## Code Review

### As a Reviewer

- Check for correctness and edge cases
- Verify tests cover changes
- Ensure code follows style guidelines
- Check for performance implications
- Verify documentation is updated

### Addressing Feedback

- Respond to all comments
- Make requested changes in new commits
- Mark conversations as resolved when addressed
- Re-request review when ready

## Release Process

Releases are automated via Changesets:

1. **Merge PRs with changesets** to `main`
2. **Changeset bot** creates a "Version Packages" PR
3. **Review and merge** the Version PR
4. **Packages are released** automatically

## Getting Help

- **Slack**: #dcoder-platform
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Docs**: `/docs` directory

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (PROPRIETARY - Deloitte).

