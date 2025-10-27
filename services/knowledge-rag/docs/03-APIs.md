 # APIs
 
 Global conventions: headers and error envelope per Service Contracts.
 
 Endpoints
 - GET `/health`, `/health/ready`, `/health/live`
 - POST `/v1/rag/ingest`
   - Request: multipart form or `{ source: url|s3|upload, metadata? }`
   - Response: `{ jobId }`
 - GET `/v1/rag/ingest/{jobId}` → status
 - POST `/v1/rag/search`
   - Request: `{ query, topK?: number, filters?: { ... } }`
   - Response: `{ items: [{ text, score, source, chunkId, citation }], nextCursor? }`
 - POST `/v1/rag/answer`
   - Request: `{ question, topK?, filters?, llm?: { model } }`
   - Response: `{ answer, citations: [{ text, source, chunkId }] }`
 
 Security: JWT via Platform API; tenant headers required.
 
 References: [Service Contracts](../../../docs/project-docs/releases/R1/SERVICE_CONTRACTS.md)
