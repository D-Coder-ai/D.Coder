 # Integrations
 
 Consumes
 - Provider APIs (OpenAI/Anthropic/Google/Groq)
 - Redis for cache; PostgreSQL for keys
 
 Exposes
 - OpenAI-compatible API to Platform via Kong-bypassed route (direct port 4000)
 - Metrics to monitoring stack
 
 References: [Architecture](../../../docs/project-docs/releases/R1/ARCHITECTURE.md)
