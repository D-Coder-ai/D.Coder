# Plugin Architecture — R3

- Residency-aware tasks: plugins must honor tenant region and egress rules
- Guarded actions: destructive operations require policy checks and audit
- Secrets still via Vault/KMS `secretRef`
