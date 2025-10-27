 # Testing and Observability
 
 Testing
 - Unit: plugin adapters and webhook validators
 - Integration: roundtrips to sandbox APIs (mocked if needed)
 - E2E: enable plugin → receive webhook → event emitted
 
 Observability
 - Metrics: webhook rate, failures, job durations
 - Tracing: external API spans; correlation via request IDs
 - Health: `/health*`
