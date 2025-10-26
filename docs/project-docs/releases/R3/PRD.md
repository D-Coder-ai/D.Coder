# Release R3 (Early Access, EA) — Product Requirements Document (PRD)

Platform: D.Coder

Primary Tenant: Deloitte USI IGS

Status: Planning — Documentation-First

## 1. Goals
- Achieve EA‑level security and compliance posture (SOC2‑ready scope).
- Enforce guardrails with block‑on‑detection policies.
- Deliver data residency/egress controls and offboarding runbook.

## 2. Scope (Functional)
- Guardrails: Prompt‑injection/DLP block policies with exemptions and audit.
- Data Egress & Residency
  - Regional data storage options; egress allowlists per region/tenant.
  - Air‑gap deployment mode design.
- Offboarding/Kill Switch
  - Sequence: IdP deprovision → revoke app tokens → disable Kong consumer → flush caches → pause jobs.
- Semantic Cache Policy
  - Namespacing by tenant+provider+model; TTL‑based invalidation; per‑tenant opt‑out.

## 3. Scope (Non‑Functional)
- Compliance documentation (SOC2 controls mapping; retention policies; DR/backup encryption).
- Pen‑test and remediation backlog creation.

## 4. Acceptance Criteria
- Guardrail blocks enforced with auditable overrides.
- Residency/egress controls configured per tenant; air‑gap design documented.
- Offboarding runbook validated in staging.
- Cache isolation policy implemented and documented.


