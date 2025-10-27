 # Security and Guardrails
 
 - JWT auth via Platform API; ABAC enforced upstream
 - Quotas: rate limits at Kong; per-tenant budgets tracked by Platform API
 - Guardrails: detect-only; log potential sensitive document ingestion
 - Audit: structured logs; correlation IDs propagated
