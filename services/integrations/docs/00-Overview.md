 # Integrations — R1 Overview
 
 Purpose: Plugin-based connectors (Jira, Bitbucket, Confluence, SharePoint) enabling external data flow and agent actions.
 
 In scope (R1)
 - Plugin scaffold with enable/disable per tenant (Flagsmith)
 - Webhook ingestion and signature validation
 - Basic connector stubs (Jira issue fetch/comment, Bitbucket PR list, Confluence/SharePoint page fetch)
 - Event-driven sync and tool exposure via MCP
 
 Out of scope (R1)
 - Full bi-directional sync, complex workflows, enterprise rate controls
 
 Quickstart
 - Port: 8085
 - Health: GET /health
 - Start: docker-compose up -d
 
 Success: Plugins discoverable/toggleable; minimal actions succeed; events emitted.
 
 References: [PRD](../../../docs/project-docs/releases/R1/PRD.md) • [Architecture](../../../docs/project-docs/releases/R1/ARCHITECTURE.md) • [Plugin Architecture](../../../docs/project-docs/releases/R1/PLUGIN_ARCHITECTURE.md) • [Service Contracts](../../../docs/project-docs/releases/R1/SERVICE_CONTRACTS.md)
