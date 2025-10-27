 # Security and Guardrails
 
 - API key/JWT enforcement where applicable via plugins
 - Rate limiting per tenant; Redis-backed counters
 - Prompt guard/transform plugins optional (detect-only)
 - Audit via http-log; correlation-id for tracing
