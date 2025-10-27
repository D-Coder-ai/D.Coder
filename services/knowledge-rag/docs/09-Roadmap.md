 # Roadmap (R1)
 
 KR-001 API skeleton (ingest/search) [AC: /v1/rag/* live]
 - KR-001a Health + routers
 - KR-001b OpenAPI docs
 
 KR-002 Ingestion pipeline (Unstructured) [AC: job runs]
 - KR-002a Storage adapters (MinIO)
 - KR-002b Chunking strategy
 
 KR-003 Indexing with pgvector [AC: hybrid retrieval works]
 - KR-003a Schema + migrations
 - KR-003b Embedding provider wiring
 
 KR-004 Retrieval API with citations [AC: citations present]
 - KR-004a Rerank optional
 
 KR-005 Events: ingestion.* index.* [AC: schema validated]
 - KR-005a JetStream setup
 
 KR-006 Observability + health [AC: metrics exported]
 - KR-006a Prometheus + OTel
