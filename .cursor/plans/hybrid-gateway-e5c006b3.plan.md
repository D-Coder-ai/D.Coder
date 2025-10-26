<!-- e5c006b3-b449-4ae8-85e7-18c5705431ac 8449091c-debe-49d9-b174-d7769f4144fc -->
# Hybrid Gateway Architecture Retrofit - R1

## Context

Task 1 currently has 6/12 subtasks completed, implementing Kong for LLM routing with memory-based caching. However, Kong OSS has significant limitations:

- No Redis-backed semantic caching in DB-less mode
- No prompt compression without Enterprise plugins
- Complex Lua scripting required for LLM-specific features
- Risk of more features moving to Enterprise tier

**Solution**: Adopt hybrid architecture with Kong (platform services) + LiteLLM Proxy (LLM traffic) inspired by `docs/project-docs/updates/hybrid-gateway-architecture-litellm-integration.md`.

## Architecture Changes

### Current (Kong-Only)

```
Client → Platform API → Kong Gateway → LLM Providers
```

### New (Hybrid)

```
Client → Platform API ─┬─→ Kong Gateway → Platform Services
                       └─→ LiteLLM Proxy → LLM Providers
```

## Implementation Plan

### Phase 1: Task Restructuring

**1.1 Update Task 1: Kong Gateway (Platform Services Only)**

Simplify Task 1 to focus on platform service routing:

- **Keep completed subtasks 1-2**: Core infra and provider allowlist (reusable)
- **Mark as cancelled**: Subtasks 3-6 (LLM routes, auth, cache, rate limiting for LLMs)
- **Update remaining subtasks 7-12**: Adapt for platform services instead of LLMs
- **New complexity score**: 6 (down from 9)

**Key files to modify**:

- `platform/infra/kong/kong.yaml`: Remove all 12 LLM routes, add platform service routes
- `platform/infra/kong/README.md`: Update to reflect platform-only routing
- `.taskmaster/tasks/task-1.md`: Update description and subtask statuses

**1.2 Create Task 26: LiteLLM Proxy for LLM Gateway**

New task with 10 subtasks covering:

1. LiteLLM deployment and configuration
2. Multi-provider routing (OpenAI, Anthropic, Google, Groq)
3. Redis-backed semantic caching
4. LLMLingua prompt compression middleware
5. Virtual keys for multi-tenancy
6. Cost tracking and observability
7. Guardrails integration
8. Platform API routing logic
9. Integration testing
10. Documentation

**Complexity score**: 8 (high due to compression middleware)

### Phase 2: LiteLLM Infrastructure Setup

**2.1 Create LiteLLM Service Directory**

Structure at repository root:

```
litellm-proxy/
├── Dockerfile
├── config/
│   └── litellm_config.yaml
├── middleware/
│   ├── __init__.py
│   ├── prompt_compression.py
│   └── custom_auth.py
├── requirements.txt
├── .env.example
└── README.md
```

**2.2 Docker Compose Integration**

Add to `platform/docker-compose.yml`:

```yaml
litellm-proxy:
  build:
    context: ../litellm-proxy
  ports:
    - "4000:4000"
  environment:
    OPENAI_API_KEY: ${OPENAI_API_KEY}
    ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
    GOOGLE_API_KEY: ${GOOGLE_API_KEY}
    GROQ_API_KEY: ${GROQ_API_KEY}
    REDIS_HOST: redis
    REDIS_PORT: 6379
    DATABASE_URL: postgresql://litellm:${LITELLM_DB_PASSWORD}@postgres:5432/litellm
    LANGFUSE_PUBLIC_KEY: ${LANGFUSE_PUBLIC_KEY}
    LANGFUSE_SECRET_KEY: ${LANGFUSE_SECRET_KEY}
  volumes:
    - ../litellm-proxy/config:/app/config
    - ../shared/python:/app/shared/python
  command: ["--config", "/app/config/litellm_config.yaml", "--port", "4000"]
  depends_on:
    - postgres
    - redis
  networks:
    - dcoder-network
```

### Phase 3: LiteLLM Configuration

**3.1 Model Configuration**

Create `litellm-proxy/config/litellm_config.yaml`:

```yaml
model_list:
  # OpenAI Models
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY
      rpm: 10000
      tpm: 2000000

  - model_name: gpt-4o-mini
    litellm_params:
      model: openai/gpt-4o-mini
      api_key: os.environ/OPENAI_API_KEY
      rpm: 30000
      tpm: 5000000

  # Anthropic Models
  - model_name: claude-sonnet-4-5
    litellm_params:
      model: anthropic/claude-sonnet-4-5-20250929
      api_key: os.environ/ANTHROPIC_API_KEY
      rpm: 5000

  - model_name: claude-opus-4-1
    litellm_params:
      model: anthropic/claude-opus-4-1-20250514
      api_key: os.environ/ANTHROPIC_API_KEY
      rpm: 4000

  # Google Models
  - model_name: gemini-2-5-pro
    litellm_params:
      model: gemini/gemini-2.5-pro
      api_key: os.environ/GOOGLE_API_KEY
      rpm: 15000

  - model_name: gemini-2-5-flash
    litellm_params:
      model: gemini/gemini-2.5-flash
      api_key: os.environ/GOOGLE_API_KEY
      rpm: 30000

  # Groq Models
  - model_name: groq-llama-3-3-70b
    litellm_params:
      model: groq/llama-3.3-70b-versatile
      api_key: os.environ/GROQ_API_KEY
      rpm: 30

router_settings:
  routing_strategy: cost-based-routing
  num_retries: 3
  timeout: 120
  fallbacks:
    - gpt-4o: ["claude-sonnet-4-5", "gemini-2-5-pro"]
  redis_host: redis
  redis_port: 6379

litellm_settings:
  cache: true
  cache_params:
    type: redis
    host: redis
    port: 6379
    ttl: 3600
    namespace: "litellm:cache"
  
  success_callback: ["langfuse", "prometheus"]
  callbacks: ["prompt_compression_middleware"]
  set_verbose: false
  json_logs: true

general_settings:
  master_key: ${LITELLM_MASTER_KEY}
  database_url: ${DATABASE_URL}
```

**3.2 Redis-Backed Semantic Caching**

LiteLLM provides native Redis caching with semantic similarity out of the box - no custom Lua needed.

### Phase 4: Prompt Compression Implementation

**4.1 LLMLingua Integration**

Create `litellm-proxy/middleware/prompt_compression.py`:

```python
from litellm.integrations.custom_logger import CustomLogger
from llmlingua import PromptCompressor
import litellm
from typing import Optional, Literal

class PromptCompressionMiddleware(CustomLogger):
    def __init__(self):
        super().__init__()
        self.compressor = PromptCompressor(
            model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
            device_map="cpu"
        )
        
        self.compression_config = {
            "default": {
                "enabled": True,
                "target_ratio": 0.5,  # 2x compression
                "min_tokens": 500
            },
            "rag_queries": {
                "enabled": True,
                "target_ratio": 0.33,  # 3x compression
                "min_tokens": 1000
            }
        }
    
    async def async_pre_call_hook(
        self,
        user_api_key_dict,
        cache,
        data: dict,
        call_type: Literal["completion", "embeddings"]
    ) -> Optional[dict]:
        if call_type != "completion":
            return data
        
        messages = data.get("messages", [])
        if not messages:
            return data
        
        # Compress and return modified data
        compressed_data = await self._compress_messages(messages, data)
        
        await self._log_compression_metrics(
            tenant_id=user_api_key_dict.team_id,
            original_tokens=compressed_data["original_tokens"],
            compressed_tokens=compressed_data["compressed_tokens"],
            savings_percent=compressed_data["savings_percent"]
        )
        
        return compressed_data["data"]
    
    async def _compress_messages(self, messages: list, data: dict) -> dict:
        # Implementation details from hybrid doc
        # Extract context, question, instruction
        # Apply LLMLingua compression
        # Return modified data with metrics
        pass
```

**4.2 Install Dependencies**

`litellm-proxy/requirements.txt`:

```
litellm[proxy]>=1.50.0
llmlingua>=0.2.0
prometheus-client>=0.19.0
psycopg2-binary>=2.9.0
redis>=5.0.0
```

### Phase 5: Platform API Routing Logic

**5.1 Update Platform API**

Modify `platform-api/src/routing/gateway_router.py`:

```python
class GatewayRouter:
    def __init__(self):
        self.kong_url = os.getenv("KONG_GATEWAY_URL", "http://kong-gateway:8000")
        self.litellm_url = os.getenv("LITELLM_PROXY_URL", "http://litellm-proxy:4000")
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def route_request(self, request: Request, user: User, endpoint: str):
        gateway = self._select_gateway(endpoint)
        
        if gateway == "litellm":
            target_url = f"{self.litellm_url}{endpoint}"
            headers = self._build_litellm_headers(request, user)
        else:
            target_url = f"{self.kong_url}{endpoint}"
            headers = self._build_kong_headers(request, user)
        
        response = await self.client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=await request.body()
        )
        
        return response
    
    def _select_gateway(self, endpoint: str) -> Literal["kong", "litellm"]:
        llm_prefixes = [
            "/v1/chat/completions",
            "/v1/completions",
            "/v1/embeddings"
        ]
        
        for prefix in llm_prefixes:
            if endpoint.startswith(prefix):
                return "litellm"
        
        return "kong"
```

### Phase 6: Kong Simplification

**6.1 Update Kong Configuration**

Replace LLM routes in `platform/infra/kong/kong.yaml` with platform service routes:

```yaml
services:
  - name: platform-api
    url: http://platform-api:8082
    routes:
      - name: platform-api-route
        paths: [/v1/tenants, /v1/providers, /v1/quotas, /v1/usage]
  
  - name: agent-orchestrator
    url: http://agent-orchestrator:8083
    routes:
      - name: agent-route
        paths: [/v1/agents, /v1/workflows]
  
  - name: knowledge-rag
    url: http://knowledge-rag:8084
    routes:
      - name: knowledge-route
        paths: [/v1/knowledge, /v1/documents]
  
  # Remove all llm.* routes
```

### Phase 7: Testing & Validation

**7.1 Integration Tests**

Create `litellm-proxy/tests/test_integration.py`:

- Test routing to all 4 providers
- Verify Redis caching (MISS → HIT)
- Validate compression metrics
- Check virtual key multi-tenancy
- Confirm cost tracking

**7.2 Performance Validation**

- Cache hit latency <50ms
- Compression overhead <50ms
- 2-3x compression ratio
- 40-60% cache hit rate target

### Phase 8: Documentation Updates

**8.1 Architecture Documentation**

Update `docs/project-docs/releases/R1/ARCHITECTURE.md`:

- Replace Kong AI Gateway section with hybrid architecture
- Add LiteLLM Proxy section
- Update request flow diagrams
- Document compression strategy

**8.2 Challenge Documentation**

Create `docs/challenges/hybrid-architecture-migration.md`:

- Document the migration from Kong-only to hybrid
- Reference original challenges
- Explain architecture decision
- Provide rollback procedures

**8.3 Integration Guides**

- `litellm-proxy/README.md`: Service-specific documentation
- `platform/infra/kong/README.md`: Updated for platform routing only
- Platform API routing guide

### Phase 9: Taskmaster Updates

**9.1 Update Existing Tasks**

Use Taskmaster MCP tools:

```bash
# Cancel Task 1 LLM-specific subtasks
task-master set-status --id=1.3,1.4,1.5,1.6 --status=cancelled --tag=r1-beta

# Update Task 1 description
task-master update-task --id=1 --prompt="Simplify to platform service routing only; LLM routing moved to Task 26 (LiteLLM)" --tag=r1-beta

# Update remaining subtasks 7-12 for platform services
task-master update-subtask --id=1.7 --prompt="Adapt guardrails for platform APIs instead of LLM routes" --tag=r1-beta
```

**9.2 Create Task 26**

```bash
# Add new task
task-master add-task --prompt="Deploy LiteLLM Proxy for LLM gateway with Redis caching, LLMLingua compression, multi-provider routing, virtual keys, and Platform API integration" --priority=high --dependencies=1,3 --tag=r1-beta

# Expand into subtasks
task-master expand --id=26 --num=10 --tag=r1-beta
```

**9.3 Update Complexity**

```bash
# Analyze new complexity
task-master analyze-complexity --ids=1,26 --tag=r1-beta

# Review report
task-master complexity-report --tag=r1-beta
```

## Key Benefits

1. **No Vendor Lock-in**: 100% OSS with no Enterprise license needed
2. **Better LLM Features**: Native semantic caching, compression, cost routing
3. **70% Cost Reduction**: Caching (40-60%) + Compression (20-30%)
4. **Simplified Maintenance**: Purpose-built tools vs custom Lua
5. **Future-Proof**: Can evolve each gateway independently

## Rollback Strategy

If issues arise:

1. Route Platform API back to Kong for LLM traffic (1-line change)
2. Keep LiteLLM running but unused
3. Re-enable Kong LLM routes from git history
4. Investigate LiteLLM issue offline
5. Fix and redeploy when ready

**Rollback time**: <5 minutes

## Implementation Sequence

1. Create litellm-proxy directory structure
2. Install LiteLLM and dependencies
3. Configure model list and caching
4. Implement compression middleware
5. Update Platform API routing
6. Simplify Kong to platform services
7. Integration testing
8. Update Taskmaster tasks
9. Update documentation
10. Deploy and monitor

## Dependencies Resolution

- Research LiteLLM latest docs: Use context7 MCP (`mcp_context7_get-library-docs` with `/BerriAI/litellm`)
- Research LLMLingua: Use exa MCP (`mcp_exa_get_code_context_exa` for implementation examples)
- Validate approach: Use web search for recent best practices

## Success Criteria

- ✅ LiteLLM proxy running and healthy
- ✅ All 4 providers routing correctly
- ✅ Redis caching operational (>40% hit rate)
- ✅ Compression achieving 2-3x ratio
- ✅ Kong handling platform services only
- ✅ Platform API routing to both gateways
- ✅ All tests passing
- ✅ Documentation updated
- ✅ Taskmaster tasks reflect new structure

### To-dos

- [ ] Research LiteLLM documentation using context7 MCP for latest API and middleware patterns
- [ ] Research LLMLingua implementation examples using exa MCP for compression strategies
- [ ] Create litellm-proxy directory with Dockerfile, config, middleware, and requirements
- [ ] Implement LLMLingua compression middleware with configurable ratios and metrics
- [ ] Configure litellm_config.yaml with all models, Redis caching, and callbacks
- [ ] Add litellm-proxy service to platform/docker-compose.yml with proper networking
- [ ] Implement gateway routing logic in Platform API to split LLM vs platform traffic
- [ ] Remove LLM routes from Kong config and add platform service routes
- [ ] Use Taskmaster to cancel Task 1 subtasks 3-6 and update descriptions
- [ ] Create Task 26 for LiteLLM with 10 subtasks using Taskmaster
- [ ] Create and run integration tests for LiteLLM routing, caching, and compression
- [ ] Run Taskmaster complexity analysis on Tasks 1 and 26
- [ ] Update R1/ARCHITECTURE.md and create hybrid-architecture-migration.md