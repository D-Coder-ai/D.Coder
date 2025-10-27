 # Architecture
 
 Components
 - FastAPI API (port 8085)
 - Plugin manager (load, enable/disable, per-tenant config)
 - Workers (Celery + Redis) for async jobs
 - Event bus (NATS JetStream)
 
 Sequence
 - Webhook → validate → enqueue → worker executes → publish `integration.*`
 - Agent tool call → plugin adapter → external API → normalized response
 
 Data
 - Minimal state; per-tenant plugin config; caches
 
 References: [Plugin Architecture](../../../docs/project-docs/releases/R1/PLUGIN_ARCHITECTURE.md)
