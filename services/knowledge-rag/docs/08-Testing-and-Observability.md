 # Testing and Observability
 
 Testing
 - Unit: chunking, embedding adapters, ranking
 - Integration: ingestion workflow with Unstructured + pgvector
 - E2E: ingest sample corpus, search, and answer with citations
 
 Observability
 - Metrics: ingestion throughput, index size, search latency
 - Tracing: parse→embed→upsert spans; search pipeline spans
 - Health: `/health*`
