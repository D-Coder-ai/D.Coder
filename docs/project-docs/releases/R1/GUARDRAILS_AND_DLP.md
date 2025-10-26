# Guardrails and DLP Policy — R1

## R1 (MVP)
- Detection only (alert): prompt injection, sensitive data exfiltration, jailbreak patterns.
- PII redaction at observability sinks where feasible.
- Tool allowlists by tenant.

## R3 (EA)
- Block-on-detection with auditable overrides and tenant policies.
- Model/tool-specific guardrail exemptions with expiry.

## Implementation Notes
- Candidate libraries: LlamaGuard, LLM Guard, Rebuff; select per performance and maintainability.
- Logs contain redacted artifacts; detailed payloads gated by roles.
