 # Configuration
 
 Env vars
 - `PORT=8085`
 - `REDIS_URL` (Celery) `NATS_URL`
 - `PLATFORM_API_BASE` `KONG_BASE_URL`
 - Provider credentials via tenant config, not env (BYO)
 
 Feature flags
 - `integrations.plugin.<key>.enabled`
 - `integrations.webhook.strict_validation`
 
 References: [Configuration Model](../../../docs/project-docs/releases/R1/CONFIGURATION.md)
