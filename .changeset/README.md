# Changesets

This directory contains changeset files for version management in the D.Coder monorepo.

## Creating a Changeset

When making changes to services or packages, create a changeset:

```bash
pnpm changeset
```

Follow the prompts to:
1. Select which packages changed
2. Choose the version bump type (major, minor, patch)
3. Provide a summary of the changes

## Versioning

Changesets are consumed during the release process:

```bash
pnpm version-packages  # Updates versions and CHANGELOGs
pnpm release           # Publishes packages (internal only)
```

## Workflow

1. **PR Creation**: Include changeset file in your PR
2. **PR Review**: Reviewer validates changeset appropriateness
3. **Merge**: Changeset is merged to main
4. **Release**: Automated release workflow processes changesets

## Learn More

- [Changesets Documentation](https://github.com/changesets/changesets)
- [Monorepo Versioning Guide](../docs/runbooks/monorepo-workflow.md)

