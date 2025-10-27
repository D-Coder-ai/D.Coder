 # Architecture
 
 - LiteLLM server exposing OpenAI-compatible routes
 - Middleware: semantic cache (Redis), prompt compression
 - Config-driven model list and routing strategy
 - Cost tracking with per-tenant virtual keys (PostgreSQL)
 
 Request flow: Client → Platform API → LiteLLM → Provider
 
 References: [LiteLLM Docs](https://docs.litellm.ai/) • [Service README](../README.md)
