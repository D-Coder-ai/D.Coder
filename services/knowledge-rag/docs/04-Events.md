 # Events
 
 Envelope per Service Contracts.
 
 Published
 - `ingestion.started` `{ jobId, source, counts }`
 - `ingestion.completed` `{ jobId, docs, chunks, errors? }`
 - `index.updated` `{ corpusId, added, updated, deleted }`
 
 Subscribed
 - `integration.sync.completed` to trigger re-index
 
 References: [Service Contracts](../../../docs/project-docs/releases/R1/SERVICE_CONTRACTS.md)
