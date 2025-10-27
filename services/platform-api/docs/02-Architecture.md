 # Architecture
 
 - Hexagonal architecture (domain, application, adapters, infrastructure)
 - Persistence: PostgreSQL; Redis cache; Alembic migrations
 - Auth: Logto OIDC; ABAC via Casbin
 - Events: NATS JetStream
 
 Request flow: Client → Kong → Platform API → services or LiteLLM per need
 
 References: [Service README](../README.md)
