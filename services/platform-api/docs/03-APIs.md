 # APIs (selected)
 
 Global conventions apply.
 
 Health
 - `GET /health` `/health/ready` `/health/live`
 
 Tenants
 - `GET /v1/tenants` `POST /v1/tenants` `GET/PATCH/DELETE /v1/tenants/{id}`
 
 Users
 - `GET/POST /v1/users` `GET/PATCH/DELETE /v1/users/{id}`
 
 Quotas
 - `GET /v1/quotas` `PUT /v1/quotas` `GET /v1/quotas/usage`
 
 Providers
 - `GET /v1/providers` `PUT/DELETE /v1/providers/{provider}` `POST /v1/providers/{provider}/test`
 
 Auth
 - `POST /v1/auth/login|logout|refresh`
 
 Error envelope and headers per Service Contracts.
