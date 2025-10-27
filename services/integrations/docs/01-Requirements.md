 # Requirements (R1)
 
 Functional
 - Plugin registry and lifecycle (enable/disable per tenant)
 - Webhook endpoints with HMAC verification
 - Minimal connectors: Jira (get issue, comment), Bitbucket (list PRs), Confluence/SharePoint (pull page)
 - Publish integration events; expose MCP tools for agent use
 
 Non-functional
 - Async execution (Celery workers)
 - Backoff/retry for API limits; idempotent handlers
 - Observability: metrics, traces, logs
 
 Inputs/Outputs
 - Inputs: webhooks, scheduled sync triggers, agent tool calls
 - Outputs: normalized entities, events `integration.*`, tool responses
 
 References: PRD • Architecture • Plugin Architecture
