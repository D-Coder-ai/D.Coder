 # Integrations
 
 Consumes
 - LiteLLM Proxy for embeddings (if not local)
 - Integrations service for source connectors (Jira/Confluence/SharePoint)
 
 Exposes
 - RAG APIs proxied via Kong
 - Events to inform other services for grounding availability
 
 Call rules
 - Outbound model calls can go to LiteLLM; all HTTP via Kong otherwise
 - Include global headers
 
 References: [Architecture](../../../docs/project-docs/releases/R1/ARCHITECTURE.md)
