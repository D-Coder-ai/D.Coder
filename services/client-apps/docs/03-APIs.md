 # APIs (Consumption)
 
 The clients do not expose server APIs in R1; they consume:
 - Platform API `/v1/*` via Kong
 - RAG `/v1/rag/*`
 - Orchestrator `/v1/workflows/*`
 - LiteLLM OpenAI-compatible endpoints for chat/completions
 
 Headers and error handling follow global conventions.
