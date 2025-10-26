# Offboarding / Kill Switch — Runbook (R3)

Sequence:
1) IdP deprovision (Logto)
2) Revoke application tokens
3) Disable Kong consumer / credentials
4) Flush caches (semantic + session)
5) Pause/cancel background jobs
6) Archive data per retention; disable integrations

Verification:
- Events emitted; audit entries present
