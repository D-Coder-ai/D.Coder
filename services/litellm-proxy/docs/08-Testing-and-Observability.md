 # Testing and Observability
 
 Testing
 - Unit: middleware (cache/compression)
 - Integration: provider calls with mocks
 - E2E: chat completion with cache hit/miss assertions
 
 Observability
 - Prometheus metrics (request duration, tokens, cache hit rate, compression savings)
 - Langfuse traces
 - Health: `/health`
