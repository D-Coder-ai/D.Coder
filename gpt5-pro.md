# gpt5-pro.md — R1 Structure Review & Fixes Plan

## Alignment Summary

- Hybrid gateway: Kong (platform APIs) + LiteLLM Proxy (LLM). No Kong AI Gateway.
- Prompt compression: custom middleware at `services/litellm-proxy/middleware/`; LLMLingua optional library.
- Semantic cache: owned by LiteLLM (Redis), not Kong.
- Monorepo: macro-services under `services/`, infra under `infrastructure/`, shared libs in `packages/`.

## Observations (concise)

1. LiteLLM compression: no native prompt compression found; LLMLingua documented; repo has custom middleware.
2. Compose paths: `infrastructure/docker-compose.base.yml` references `./gateways/*` (mismatch). Should reference `../services/*` or relocate.
3. Duplicate compose: central compose + per-service composes (`services/kong-gateway/docker-compose.yml`, etc.). Risk of drift.
4. Semantic cache: docs occasionally attribute to Kong; should be LiteLLM Redis cache.
5. `.env.example`: missing at repo root; compose/env vars not documented.
6. Naming: `kong` vs `kong-gateway` across docs/compose. Inconsistent.
7. `ARCHITECTURE.md`: duplicated sections; repeated blocks; outdated links.
8. Repo structure: docs show `platform/*` and `apps/infra`; actual is `services/` + `infrastructure/`.
9. Wrong paths: many `platform/infra/*` and `platform/gateways/*` references in docs.

## Targeted Fixes (docs-only; no code moves)

- ~~PRD (`docs/project-docs/releases/R1/PRD.md`)
  - Switch “Kong AI Gateway” → “Hybrid gateway (Kong + LiteLLM)”. Clarify no auto failover.~~
- ~~Service Contracts (`docs/project-docs/releases/R1/SERVICE_CONTRACTS.md`)
  - Rename section to “AI Gateway (Hybrid: Kong + LiteLLM)”. Note quotas at LiteLLM and mirrored to Platform API. Route namespace split: LiteLLM for provider routes, Kong for platform APIs.~~
- ~~Architecture Guide (`docs/project-docs/releases/R1/ARCHITECTURE.md`)
  - Make hybrid split explicit; remove mentions of semantic cache in Kong; state Redis cache in LiteLLM.
  - Fix duplicate sections; fix link to `docs/project-docs/updates/hybrid-gateway-architecture-litellm-integration.md`.
  - Replace repo tree with actual `services/`, `infrastructure/`, `packages/`, `tools/`.~~
- ~~Architecture Addendum (`docs/project-docs/releases/R1/ARCHITECTURE_ADDENDUM.md`)
  - Correct cross-refs to `./CONFIGURATION.md` and `./PLUGIN_ARCHITECTURE.md`. Reiterate R1 guardrails alert-only, no auto failover.~~
- ~~Configuration (`docs/project-docs/releases/R1/CONFIGURATION.md`)
  - Clarify platform vs tenant settings; reference `infrastructure/policies/allowed_provider_hosts.yaml`; reference LiteLLM config at `services/litellm-proxy/config/`.~~
- ~~Plugin Architecture (`docs/project-docs/releases/R1/PLUGIN_ARCHITECTURE.md`)
  - Note Flagsmith enablement and plugin stubs live under `services/integrations/`.~~
- ~~Compose docs (short note in `ARCHITECTURE.md`)
  - Standardize central orchestration under `infrastructure/docker-compose.base.yml` (+ `docker-compose.dev.yml`). Mark per-service compose as local-dev only to avoid drift.
  - Fix compose path references from `./gateways/*` → `../services/kong-gateway` and `../services/litellm-proxy`.~~
- ~~Naming normalization
  - Use “Kong Gateway” (service: `kong-gateway`) consistently in docs. Keep container names as-is.~~
- ~~Add `.env.example` (repo root)
  - Include keys referenced by compose/services: `POSTGRES_*`, `REDIS_*`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `GROQ_API_KEY`, `LITELLM_MASTER_KEY`, `LANGFUSE_*`, `FLAGSMITH_*`, `GRAFANA_*`, `LOG_LEVEL`, etc.~~

## Rationale per additional checks

- LiteLLM compression: LiteLLM docs cover caching only; no native compression. LLMLingua remains external; our custom middleware path exists.
- Compose paths/duplicates: central compose uses non-existent `./gateways/*` paths; per-service compose files can drift from main config.
- Semantic cache: all caching responsibilities should be documented under LiteLLM proxy.
- `.env.example`: absent; developers lack template for required variables.
- Naming: maintain `kong-gateway` consistently to avoid confusion across services/docs.
- `ARCHITECTURE.md`: prune repeated sections and fix outdated references.
- Repo structure & paths: ensure docs reflect `services/` + `infrastructure/` (post-migration) instead of legacy `platform/*` references.

## Next Actions

- Keep this plan as the authoritative fix list for R1 alignment.
- Execute doc edits above in a dedicated docs-only change (outside the scope of this document).

