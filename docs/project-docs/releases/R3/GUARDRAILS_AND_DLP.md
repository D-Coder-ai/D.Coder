# Guardrails and DLP — R3

## Mode: block
- Enforce block-on-detection; configurable per tenant
- Overrides: time-bound, auditable, least privilege

## Signals
- Prompt injection, DLP patterns, jailbreaks; tool allowlists

## Audit & Observability
- Emit `guardrail.blocked` with redacted context; dashboards include block rates
