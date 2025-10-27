 # APIs
 
 Global conventions apply.
 
 Endpoints
 - GET `/health`
 - GET `/v1/integrations/plugins` → list plugins and tenant enablement
 - POST `/v1/integrations/plugins/{key}:enable` `{ enabled: boolean }`
 - POST `/v1/integrations/webhooks/{provider}` → webhook receiver
 - POST `/v1/integrations/jira/issues/{key}/comment` `{ body }`
 - GET `/v1/integrations/bitbucket/repos/{repo}/pulls`
 - GET `/v1/integrations/{provider}/pages/{id}`
 
 Security
 - JWT required; per-tenant plugin permissions checked
 - Webhooks: HMAC signature headers
 
 References: [Service Contracts](../../../docs/project-docs/releases/R1/SERVICE_CONTRACTS.md)
