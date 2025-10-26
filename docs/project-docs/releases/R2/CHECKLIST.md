# R2 Agent Handoff Checklist

- [ ] Read PRD and Architecture Addendum
- [ ] Load ARCHITECTURE.md and SERVICE_CONTRACTS.md
- [ ] Configure providers via secretRef (Vault/KMS)
- [ ] Enable archival with retention settings
- [ ] Guardrails set to detect-only
- [ ] Update events: conversation.archived
- [ ] Validate quotas at gateway and API counters
