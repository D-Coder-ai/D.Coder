# Release R2 (Release Preview) — Product Requirements Document (PRD)

Platform: D.Coder

Primary Tenant: Deloitte USI IGS

Status: Planning — Documentation-First

## 1. Goals
- Add foundational security/compliance features while maintaining MVP velocity.
- Introduce prompt IP protection (envelope encryption) and conversation archival.
- Keep deployment flexible; no local inference requirement.

## 2. Scope (Functional)
- Prompt IP Security
  - Per‑tenant KEK in Vault/KMS; DEK per secret; AES‑GCM; rotation every 90 days.
  - Runtime-only decryption; in‑memory lifetime minimized.
- Conversation Archival
  - Retention configurable per tenant; default 1–3 years.
  - Encrypted at rest; export API with audit logging.
- Guardrails
  - Maintain alert‑only detection; prepare policies for block in R3.
- Governance
  - Budget alerts/escalations; improved quota reconciliation.

## 3. Scope (Non‑Functional)
- Compliance mapping (SOC2 focus): begin documenting control alignment.
- Audit trail hardening: signed hash chains for critical ops.
- Observability expansions: add redaction in logs; trace sampling policies.

## 4. Out of Scope (R2)
- Data residency/air‑gap posture.
- Offboarding/kill switch runbook.
- Semantic cache isolation policy.

## 5. Acceptance Criteria
- Prompts stored encrypted with per‑tenant KEK/DEK scheme; rotation docs published.
- Conversation archival enabled with configurable retention and export.
- Audit trail and observability updated per scope.
- Documentation: R2 PRD, R2 Architecture Addendum, security design notes.


