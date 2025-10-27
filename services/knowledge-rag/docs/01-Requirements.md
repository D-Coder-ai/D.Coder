 # Requirements (R1)
 
 Functional
 - Ingest documents from file upload and connectors (future via Integrations)
 - Parse with Unstructured; store artifacts; create embeddings
 - Index in pgvector; enable BM25 + dense retrieval
 - Serve search and answer-with-citations APIs
 - Emit ingestion/indexing lifecycle events
 
 Non-functional
 - Tenant isolation by database; no cross-tenant sharing
 - Observability with Prometheus/OTel
 - Backpressure on large ingestions; idempotent jobs
 
 Inputs/Outputs
 - Inputs: documents (binary/text), queries, filters
 - Outputs: search results, answers, citations, events `ingestion.*`, `index.*`
 
 References: PRD • Architecture • Service Contracts • Configuration
