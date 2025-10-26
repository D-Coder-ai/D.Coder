# Release R2 (Release Preview) — Architecture Addendum

## Security & Compliance Enhancements
- Prompt IP Protection: Envelope encryption using per‑tenant KEKs (Vault/KMS), DEK per secret, AES‑GCM. Rotation every 90 days.
- Runtime Decryption: Secrets decrypted on demand; DEKs never written to disk.
- Conversation Archival: Encrypted at rest, tenant‑configurable retention, export with audit entries.

## Observability & Audit
- Redaction policies for logs and traces.
- Signed hash chain for critical audit events.

## Guardrails
- Detection remains alert‑only in R2; block-on-detection planned for R3.

## Documentation Cross‑References
- R2 PRD: ./PRD.md
- Security design: ../security/PROMPT_ENCRYPTION.md (to be authored)


