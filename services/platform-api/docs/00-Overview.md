 # Platform API — R1 Overview
 
 Purpose: Core platform capabilities — multi-tenancy, authentication/authorization, quotas, provider configs, feature flags.
 
 In scope (R1)
 - Tenants, Users, Quotas, Providers CRUD
 - JWT auth (Logto), ABAC (Casbin)
 - Usage tracking and reconciliation with LiteLLM
 - Feature flags via Flagsmith
 
 Out of scope (R1)
 - Prompt encryption (R2 plan); residency policies (R3)
 
 Quickstart
 - Port: 8082; Health: `/health*`; Docs: `/docs` when DEBUG=true
 - DB per tenant; Alembic migrations
 
 References: [Service README](../README.md) • [PRD](../../../docs/project-docs/releases/R1/PRD.md) • [Architecture](../../../docs/project-docs/releases/R1/ARCHITECTURE.md)
