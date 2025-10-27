 # Configuration
 
 Env vars
 - `PORT=8083`
 - `TEMPORAL_HOST` `TEMPORAL_NAMESPACE`
 - `NATS_URL`
 - `PLATFORM_API_BASE` (via Kong) `KONG_BASE_URL`
 - `LITELLM_BASE=http://localhost:4000`
 - `OTEL_EXPORTER_OTLP_ENDPOINT` `PROMETHEUS_PORT`
 
 Flagsmith (examples)
 - `agents.plan_review_enabled` (global)
 - `agents.integration_plugins` (tenant segment)
 
 Config sources: see [Configuration Model](../../../docs/project-docs/releases/R1/CONFIGURATION.md)
