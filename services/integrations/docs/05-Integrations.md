 # Integrations
 
 Consumes
 - External SaaS APIs (Jira, Bitbucket, Confluence, SharePoint)
 - Platform API for tenant configs and secrets (BYO credentials)
 
 Exposes
 - Webhook endpoints and plugin APIs via Kong
 - MCP tool interfaces for Agent Orchestrator
 
 Call rules
 - Outbound external calls bypass Kong; platform calls go via Kong
 - Strict header propagation; redact secrets in logs
