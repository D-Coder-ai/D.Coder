 # Architecture
 
 Components
 - FastAPI service (port 8084)
 - Ingestion workers: parse via Unstructured, chunk, embed
 - Storage: PostgreSQL (metadata + pgvector); MinIO for raw artifacts
 - Retrieval: BM25 + vector search; rerank optional
 
 Sequence
 1) Upload/ingest request accepted; job created
 2) Worker parses and chunks; embeddings computed; index upsert
 3) Search: query → hybrid retrieval → optional rerank → answer with citations
 
 References: [Architecture](../../../docs/project-docs/releases/R1/ARCHITECTURE.md)
