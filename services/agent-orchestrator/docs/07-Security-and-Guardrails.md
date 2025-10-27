 # Security and Guardrails
 
 AuthN/AuthZ
 - JWT issued via Platform API/Logto; ABAC enforced downstream
 - Service-to-service requests signed via API keys where applicable
 
 Guardrails (R1 detect-only)
 - Prompt injection detection logged; no hard blocking
 - Budget-aware behavior via `quota.updated` events (soft alerts)
 
 Quotas
 - Rate limits at Kong; include tenant headers for mirroring to Platform API
 
 Audit
 - Correlation via `X-Request-Id` and `X-Trace-Id`; structured JSON logs
