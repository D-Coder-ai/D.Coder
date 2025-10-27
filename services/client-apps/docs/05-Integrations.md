 # Integrations
 
 Consumes
 - Platform API for tenancy, quotas, providers, and usage
 - RAG for doc/code grounding
 - Orchestrator for complex tasks
 - LiteLLM for model calls (proxied)
 
 Routing
 - All traffic via Kong; cookies/tokens handled by frontend; attach headers
 
 References: [Architecture](../../../docs/project-docs/releases/R1/ARCHITECTURE.md)
