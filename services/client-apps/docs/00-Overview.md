 # Client Apps — R1 Overview
 
 Purpose: User interfaces (Open WebUI for Doc/Code Chat), Admin dashboard (Next.js), Deloitte dashboard.
 
 In scope (R1)
 - Two Open WebUI instances (Doc Chat, Code Chat)
 - Admin dashboard skeleton with auth and basic KPIs
 - Deloitte dashboard MVP
 
 Out of scope (R1)
 - Advanced workflows and custom plugins beyond MVP
 
 Quickstart
 - Ports: 3000–3004
 - Auth: Logto via Platform API
 - Routing: All API traffic through Kong; LLM via LiteLLM
 
 Success: Users can sign in, chat (grounded via RAG), and view basic KPIs.
 
 References: [PRD](../../../docs/project-docs/releases/R1/PRD.md) • [Architecture](../../../docs/project-docs/releases/R1/ARCHITECTURE.md)
