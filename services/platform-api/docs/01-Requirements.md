 # Requirements (R1)
 
 Functional
 - Multi-tenant management (DB-per-tenant provisioning)
 - Auth (Logto) + ABAC (Casbin)
 - Quotas: define, track, reconcile with LiteLLM `quota.updated`
 - Provider configurations (OpenAI, Anthropic, Google, Groq) BYO per tenant
 - Feature flags (Flagsmith) per tenant
 
 Non-functional
 - Observability: metrics, traces, structured logs
 - Security: encryption at rest for secrets, audit logging
 
 Inputs/Outputs
 - REST APIs under `/v1/*`
 - Events: `tenant.*`, `quota.*`
 
 References: Service README • PRD • Architecture • Service Contracts
