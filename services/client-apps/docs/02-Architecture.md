 # Architecture
 
 Components
 - Open WebUI (Doc/Code Chat)
 - Admin Dashboard (Next.js + TanStack Table)
 - Deloitte Dashboard (Next.js)
 
 Data flow
 Client → Kong → Platform API/Services, and → LiteLLM for LLM calls
 
 Auth
 - Logto OIDC; tokens stored per session; headers attached for API calls
 
 References: [Architecture](../../../docs/project-docs/releases/R1/ARCHITECTURE.md)
