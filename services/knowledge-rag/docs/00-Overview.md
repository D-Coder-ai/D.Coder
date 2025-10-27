 # Knowledge & RAG — R1 Overview
 
 Purpose: Document ingestion, indexing, and semantic/hybrid retrieval to ground LLM responses.
 
 In scope (R1)
 - Ingestion (Unstructured) → storage
 - Indexing in PostgreSQL + pgvector (MVP)
 - Hybrid retrieval (BM25 + dense) and citations
 - RAG APIs for search/answer
 
 Out of scope (R1)
 - Milvus at scale (planned upgrade), on-prem OCR, multi-region residency
 
 Quickstart
 - Port: 8084
 - Health: GET /health, /health/ready, /health/live
 - Start: docker-compose up -d
 
 Success: Sample corpus ingested; `/v1/rag/search` returns grounded answers with citations; metrics visible.
 
 References: [PRD](../../../docs/project-docs/releases/R1/PRD.md) • [Architecture](../../../docs/project-docs/releases/R1/ARCHITECTURE.md) • [Service Contracts](../../../docs/project-docs/releases/R1/SERVICE_CONTRACTS.md) • [Configuration](../../../docs/project-docs/releases/R1/CONFIGURATION.md)
