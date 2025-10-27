 # Integrations
 
 Consumes
 - LiteLLM `quota.updated` (events)
 - Flagsmith for feature flags
 
 Exposes
 - Core CRUD APIs to all services via Kong
 - Auth/SSO (Logto) integration for clients
 
 Call rules: all callers must include global headers; Platform API returns sanitized, tenant-scoped data.
