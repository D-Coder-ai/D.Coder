 # Requirements (R1)
 
 Functional
 - Execute agent graphs with steps: plan, act (tools), review
 - Persist and resume workflows (Temporal) with retries
 - Publish workflow lifecycle events; subscribe to integration signals
 - Propagate tenant/auth context headers on all outbound calls
 
 Non-functional
 - Multi-tenant safe by header isolation; no cross-tenant data mixing
 - Observability: Prometheus metrics, OpenTelemetry traces, structured logs
 - Quotas enforced at gateway; mirrored usage via events
 
 Inputs/Outputs
 - Inputs: user prompts, tool results, integration webhooks
 - Outputs: planned steps, tool invocations, final answer, events `workflow.*`
 
 Dependencies
 - Platform API (tenancy/auth, quotas)
 - Kong Gateway (routing), LiteLLM Proxy (LLM traffic)
 - NATS JetStream (events), Temporal (durable workflows)
 
 References: [PRD](../../../docs/project-docs/releases/R1/PRD.md) • [Architecture](../../../docs/project-docs/releases/R1/ARCHITECTURE.md) • [Service Contracts](../../../docs/project-docs/releases/R1/SERVICE_CONTRACTS.md) • [Configuration](../../../docs/project-docs/releases/R1/CONFIGURATION.md)
