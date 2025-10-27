 # Roadmap (R1)
 
 PAPI-001 Domain model [AC: migrations]
 - PAPI-001a Entities and value objects
 - PAPI-001b Alembic setup
 
 PAPI-002 Auth (Logto) + ABAC (Casbin) [AC: protected endpoint]
 
 PAPI-003 Tenants CRUD and provisioning [AC: DB-per-tenant created]
 
 PAPI-004 Providers config [AC: validate creds]
 
 PAPI-005 Quotas + reconciliation [AC: counters consistent]
 - PAPI-005a Listener for `quota.updated`
 - PAPI-005b Reconciliation job
 
 PAPI-006 Feature flags (Flagsmith) [AC: toggle integration]
 
 PAPI-007 Observability and health [AC: /metrics, /health]
