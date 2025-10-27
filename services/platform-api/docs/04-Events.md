 # Events
 
 Published
 - `tenant.created|updated|deleted` `{ id, org, plan }`
 - `quota.updated` `{ tenantId, usage, budget }`
 
 Subscribed
 - `quota.updated` from LiteLLM for reconciliation
 
 Envelope per Service Contracts.
