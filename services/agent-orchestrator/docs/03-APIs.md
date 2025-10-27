 # APIs
 
 Global conventions: headers `X-Request-Id`, `X-Tenant-Id`, `X-Platform-Id`, `X-User-Id`, `X-Trace-Id`, optional `Idempotency-Key`. Errors: `{ "error": { "code", "message", "details" } }`. Pagination: `?limit&cursor`.
 
 Endpoints
 - GET `/health` | 200 `{ status: "ok" }`
 - GET `/health/ready`, `/health/live`
 - POST `/v1/workflows/start` → Start a workflow
   - Request: `{ input: { ... }, options?: { workflowType, ttlSec } }`
   - Response: `{ workflowId, runId }`
 - GET `/v1/workflows/{workflowId}` → Get status
   - Response: `{ workflowId, status, result?, steps: [...] }`
 - POST `/v1/workflows/{workflowId}/signal` → External signal
   - Request: `{ type, payload }`
 
 Security
 - Requires JWT via Platform API; ABAC enforced downstream; include global headers on all requests/responses.
 
 References: [Service Contracts](../../../docs/project-docs/releases/R1/SERVICE_CONTRACTS.md)
