# D.Coder — R3 Architecture Guide

Scope: Early Access. Security/compliance focus with enforceable guardrails, residency/egress, offboarding, cache isolation.

## Snapshot
- Guardrails: block-on-detection with overrides
- Data residency & egress controls; air-gap design
- Offboarding/kill switch runbook
- Semantic cache isolation (tenant+provider+model)
- SOC2 readiness docs

## Services focus
- AI Gateway: block policies; cache namespacing; TTL and invalidation
- Platform API: residency config; offboarding orchestration endpoints
- Orchestrator: policy enforcement hooks; offboarding jobs
- Integrations: plugin policies respect residency/egress

## References
- PRD: `./PRD.md`
- Addendum: `./ARCHITECTURE_ADDENDUM.md`
- Guardrails: `./GUARDRAILS_AND_DLP.md`
- Residency/Egress: `./DATA_RESIDENCY_AND_EGRESS.md`
- Offboarding: `./OFFBOARDING_RUNBOOK.md`
- Cache: `./SEMANTIC_CACHE_POLICY.md`
- Compliance: `./COMPLIANCE_MAPPING.md`
- Agent brief: `./AGENT_ENGINEERING_BRIEF.md`
- Contracts: `./SERVICE_CONTRACTS.md`
