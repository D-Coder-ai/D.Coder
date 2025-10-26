# Prompt IP Protection — Envelope Encryption (R2 Plan)

## Scheme
- Per-tenant Key Encryption Key (KEK) in Vault/KMS.
- Data Encryption Key (DEK) per prompt bundle; AES-GCM.
- Rotate KEKs every 90 days; rewrap DEKs.

## Runtime
- Decrypt on demand; DEKs resident in memory only for operation duration.
- No DEKs persisted; strict zeroization on completion.

## Audit
- Signed hash chain for key operations and prompt access.
