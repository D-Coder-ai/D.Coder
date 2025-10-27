 # Testing and Observability
 
 Testing
 - Unit: LangGraph node logic and adapters
 - Integration: Temporal workflow execution; NATS pub/sub
 - E2E: plan→execute→review sample through Kong
 
 Observability
 - Metrics: `/metrics` Prometheus; key: workflow durations, step latency
 - Tracing: OpenTelemetry spans for each step and outbound call
 - Health: `/health`, `/health/ready`, `/health/live`
