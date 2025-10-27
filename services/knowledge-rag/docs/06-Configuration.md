 # Configuration
 
 Env vars
 - `PORT=8084`
 - `DATABASE_URL` (pg + pgvector)
 - `MINIO_ENDPOINT` `MINIO_ACCESS_KEY` `MINIO_SECRET_KEY`
 - `UNSTRUCTURED_API_URL`
 - `EMBEDDINGS_PROVIDER` and `LITELLM_BASE`
 - `OTEL_EXPORTER_OTLP_ENDPOINT` `PROMETHEUS_PORT`
 
 Feature flags
 - `rag.hybrid_default`
 - `rag.rerank_enabled`
 
 References: [Configuration Model](../../../docs/project-docs/releases/R1/CONFIGURATION.md)
