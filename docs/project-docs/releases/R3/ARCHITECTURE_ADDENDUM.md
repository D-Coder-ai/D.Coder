# Release R3 (EA) — Architecture Addendum

## Guardrails
- Move from alert‑only to enforce (block‑on‑detection) with allowlisted tools and tenant overrides.

## Data Residency & Egress
- Introduce region‑scoped data stores and egress allowlists.
- Document air‑gap mode: no external LLM egress; private endpoints only.

## Offboarding/Kill Switch
- Standard runbook covering IdP, application tokens, gateway consumers, background jobs, caches.

## Semantic Cache Isolation
- Namespaced cache keys by tenant+provider+model; default TTLs and invalidation playbook.

## Compliance
- SOC2 controls mapping published; DR/backup encryption documented and tested.


