# R2 Agent Engineering Brief

Focus: Add prompt IP encryption and conversation archival without breaking R1 seams.

## R2 Constraints
- BYO LLM per tenant; no local inference
- Detect-only guardrails; no block
- Quotas at Kong + mirrored in Platform API
- DB-per-tenant; Logto; Flagsmith

## New in R2
- Prompt IP protection (KEK/DEK, AES-GCM) — `./PROMPT_ENCRYPTION.md`
- Conversation archival with tenant retention, encrypted at rest

## Config additions
- Provider secrets via `secretRef` to Vault/KMS
- Archival: `retentionDays`, `exportEnabled`

## API/Event changes (see `./SERVICE_CONTRACTS.md`)
- Add `POST /v1/archive/export`
- Emit `conversation.archived`

## DoD
- Encrypted prompts at rest (per-tenant KEK/DEK)
- Archival pipeline documented and events emitted

## Handoff set
- `./PRD.md`, `./ARCHITECTURE_ADDENDUM.md`, `./ARCHITECTURE.md`
- `./SERVICE_CONTRACTS.md`, `./CONFIGURATION.md`
- `./PLUGIN_ARCHITECTURE.md`, `./GUARDRAILS_AND_DLP.md`, `./PROMPT_ENCRYPTION.md`
