 # Architecture
 
 Components
 - FastAPI service exposing control APIs and health probes (port 8083)
 - Temporal client for durable workflows (activity + workflow definitions)
 - LangGraph graphs for agent plans (plan/act/review)
 - NATS JetStream publisher/subscriber for workflow signals and status
 - Adapters for outbound calls via Kong (Platform API, RAG, Integrations) and LiteLLM
 
 Sequence (happy path)
 1) Client calls Platform API → Kong → Agent Orchestrator `/v1/workflows/start`
 2) Orchestrator creates Temporal workflow and LangGraph state
 3) Steps execute; tool calls go via Kong to downstream services or to LiteLLM proxy
 4) Events `workflow.started|step.completed|completed` published
 5) Result returned; metrics/traces emitted
 
 Data
 - Workflow execution state in Temporal
 - Minimal request metadata in logs/metrics only (no PII persistence)
 
 References: [Architecture](../../../docs/project-docs/releases/R1/ARCHITECTURE.md) • [Addendum](../../../docs/project-docs/releases/R1/ARCHITECTURE_ADDENDUM.md)
