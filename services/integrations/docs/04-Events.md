 # Events
 
 Published
 - `integration.sync.started|completed|failed` `{ provider, scope, stats }`
 - `integration.jira.issue.updated` `{ key, fields }`
 - `integration.bitbucket.pr.listed` `{ repo, count }`
 
 Subscribed
 - `workflow.*` to trigger callbacks
 
 Envelope per Service Contracts.
