 # Testing and Observability
 
 Testing
 - Unit: domain services and ports
 - Integration: adapters (persistence, auth, events)
 - E2E: CRUD flows and quota reconciliation
 
 Observability
 - Metrics: `/metrics` (requests, quota reconciliation)
 - Tracing: OTel spans for each endpoint and background job
 - Health: `/health*`
