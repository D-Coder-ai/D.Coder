# Plugin Architecture — R2

- Decoupled integrations; per-tenant enablement via Flagsmith
- Lifecycle: install → enable → configure → update → disable → uninstall
- Contract: capabilities manifest; config schema; standard interfaces
- Secrets: store per-tenant; use Vault/KMS via `secretRef`
- Categories: Jira/Linear, Slack/Teams, Confluence/SharePoint, Bitbucket
- Roadmap: audit logs for plugin actions; marketplace UX in R4
