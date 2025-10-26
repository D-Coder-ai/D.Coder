# Releases Overview (R1–R4)

This document summarizes scope and cross-links detailed PRDs and Architecture Addenda.

## R1 — Beta / MVP
- Focus: Core functionality, fast delivery; light security/compliance.
- Defaults: BYO LLM per tenant; no local inference; Logto; Flagsmith; DB-per-tenant; quotas at Kong+API; alert-only guardrails; providers (OpenAI, Anthropic, Google/Vertex, Groq); daily encrypted backups (RPO 24h, RTO 4h).
- Docs: [PRD](./R1/PRD.md), [Architecture Addendum](./R1/ARCHITECTURE_ADDENDUM.md)

## R2 — Release Preview
- Focus: Prompt IP encryption and conversation archival; compliance scaffolding.
- Docs: [PRD](./R2/PRD.md), [Architecture Addendum](./R2/ARCHITECTURE_ADDENDUM.md)

## R3 — Early Access (EA)
- Focus: Residency/egress controls, guardrail blocks, offboarding runbook, semantic cache isolation; SOC2 readiness.
- Docs: [PRD](./R3/PRD.md), [Architecture Addendum](./R3/ARCHITECTURE_ADDENDUM.md)

## R4 — General Availability (GA)
- Focus: Integrations marketplace UX, SLOs/DR game-days, optional auto failover, platform reuse hardening.
- Docs: [PRD](./R4/PRD.md), [Architecture Addendum](./R4/ARCHITECTURE_ADDENDUM.md)
