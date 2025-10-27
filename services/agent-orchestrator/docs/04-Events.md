 # Events (NATS JetStream)
 
 Envelope: `{ eventId, occurredAt, tenantId, platformId, correlationId, actor, payload }`
 
 Published
 - `workflow.started` `{ workflowId, runId, input }`
 - `workflow.step.completed` `{ workflowId, stepId, result, latencyMs }`
 - `workflow.error` `{ workflowId, stepId?, code, message }`
 - `workflow.completed` `{ workflowId, result, totalLatencyMs }`
 
 Subscribed
 - `integration.*` signals to influence workflows
 - `quota.updated` for budget-aware behavior (soft alerts in R1)
 
 References: [Service Contracts](../../../docs/project-docs/releases/R1/SERVICE_CONTRACTS.md)
