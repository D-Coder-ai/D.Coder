# Prompt IP Protection — R2

## Envelope Encryption
- Per-tenant KEK in Vault/KMS
- DEK per prompt bundle (AES-GCM)
- KEK rotation: 90 days; rewrap DEKs

## Runtime
- On-demand decrypt; DEKs memory-only; zeroize on use end

## Audit
- Signed hash chain around key ops and prompt access
