 # Security and Guardrails
 
 - JWT auth for APIs; HMAC verification for webhooks
 - Per-tenant enable/disable and scopes via Flagsmith
 - Rate limiting via Kong; retries with backoff for third-party APIs
 - Guardrails: detect-only; sanitize content before emitting events
