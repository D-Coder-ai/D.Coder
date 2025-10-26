# Plugin Architecture (Integrations & Connectors) — R1

## Goals
- Decouple integrations (Jira, Slack, Teams, SharePoint, Confluence, Linear, Bitbucket) from core services.
- Enable per-tenant enablement and configuration; support marketplace-like UX by GA.
- Use Flagsmith to expose plugin capabilities per platform/tenant combination.
- Keep implementation stubs within `services/integrations/` for managed rollout.

## Lifecycle
- Install → Enable → Configure → Update → Disable → Uninstall.
- Versioned plugins with semver; compatibility matrix with platform versions.

## Contract
- Capabilities manifest (scopes, events, webhooks, required secrets).
- Config schema (JSON Schema) with defaults; validation on save.
- Standard interfaces for: auth, event handling, sync jobs, webhooks, UI links.

## Configuration & Secrets
- Platform-level plugin catalog managed via Platform API configuration layer.
- Tenant-level enablement uses Flagsmith segments (feature flag `plugin.{name}`) with overrides stored in tenant DB.
- Secrets stored per tenant; reference Vault/KMS in R2+. Service stubs live in `services/integrations/src/infrastructure/secrets/`, with Flagsmith controlling enablement state per tenant.

## Feature Flags
- Flagsmith used to expose plugins by platform/tenant segments. Each plugin exposes a default-disabled flag toggled via Platform Admin UI.

## Categories
- Work Management: Jira, Linear.
- Collaboration: Slack, Teams.
- Knowledge: Confluence, SharePoint.
- Code: Bitbucket; future GitHub/GitLab.

## Roadmap
- R1: Plugin scaffold and contracts documented.
- R2: Secrets via Vault/KMS; audit logs.
- R3: Residency-aware scheduling; guarded actions.
- R4: Marketplace UX with discovery and updates.
