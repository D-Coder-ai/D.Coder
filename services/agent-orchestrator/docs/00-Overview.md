# Agent Orchestrator — R1 Overview

Purpose: Durable AI workflow execution using Temporal and LangGraph; routes tool calls, maintains state, and orchestrates multi-step agent plans.

In scope (R1):
- Plan/execute/review agent graphs (LangGraph)
- Durable workflow execution and retries (Temporal)
- Event-driven coordination via NATS JetStream
- Auth/tenancy propagation via platform headers
- Outbound calls proxied through Kong Gateway and LiteLLM Proxy

Out of scope (R1):
- Auto provider failover, hard guardrail blocking, on-prem inference

Quickstart:
- Port: 8083
- Health: GET /health, /health/ready, /health/live
- Start: docker-compose up -d (from repo root)

Success criteria:
- Sample plan→execute→review flow completes; events published to `workflow.*`; metrics and traces visible; required headers propagated on outbound calls.

References: [PRD](../../../docs/project-docs/releases/R1/PRD.md) • [Architecture](../../../docs/project-docs/releases/R1/ARCHITECTURE.md) • [Addendum](../../../docs/project-docs/releases/R1/ARCHITECTURE_ADDENDUM.md) • [Service Contracts](../../../docs/project-docs/releases/R1/SERVICE_CONTRACTS.md) • [Configuration](../../../docs/project-docs/releases/R1/CONFIGURATION.md)
