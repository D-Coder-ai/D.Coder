 # Roadmap (R1)
 
 AO-001 Bootstrap service skeleton (FastAPI + Temporal client) [AC: /health live]
 - AO-001a Project layout and config
 - AO-001b Health/readiness endpoints
 - AO-001c Docker compose stub
 
 AO-002 LangGraph integration [AC: sample echo graph runs]
 - AO-002a Define plan/act/review nodes
 - AO-002b State store integration
 
 AO-003 NATS JetStream events [AC: publish/subscribe OK]
 - AO-003a Event schemas
 - AO-003b JetStream stream/consumer setup
 
 AO-004 Tool routing and MCP adapters [AC: interfaces defined]
 - AO-004a MCP client stubs
 - AO-004b Kong-routed HTTP tools
 
 AO-005 Auth/tenancy propagation [AC: headers present]
 - AO-005a JWT validation middleware
 - AO-005b Header propagation filter
 
 AO-006 Observability [AC: /metrics exposed]
 - AO-006a OTel traces
 - AO-006b Prometheus metrics
 
 AO-007 E2E sample flow [AC: green test]
 - AO-007a Scripted test through Kong
 - AO-007b CI job
