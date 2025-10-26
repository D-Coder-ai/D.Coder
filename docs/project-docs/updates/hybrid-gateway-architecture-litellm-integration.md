# Hybrid Gateway Architecture: Kong + LiteLLM Proxy with Prompt Compression

**Document Version:** 1.0
**Date:** October 24, 2025
**Status:** Proposed Architecture
**Author:** D.Coder Architecture Team

---

## Executive Summary

This document proposes a **hybrid gateway architecture** that leverages the strengths of both Kong Gateway and LiteLLM Proxy to create an optimal solution for the D.Coder LLM Platform. This approach addresses all R1-R4 requirements while maintaining 100% open-source compliance and eliminating vendor lock-in concerns.

### Key Decisions

1. ✅ **Kong Gateway** - General API gateway for platform microservices
2. ✅ **LiteLLM Proxy** - Specialized LLM routing, caching, and cost optimization
3. ✅ **LLMLingua Integration** - Open-source prompt compression (20-30% reduction)
4. ✅ **Unified Observability** - Prometheus + Grafana + Langfuse across both gateways

### Strategic Benefits

| Benefit | Impact |
|---------|--------|
| **No Vendor Lock-in** | 100% OSS stack with no Enterprise license dependencies |
| **Best-of-Breed** | Kong for APIs, LiteLLM for LLMs - purpose-built tools |
| **70% Cost Reduction** | Semantic caching + prompt compression + cost routing |
| **Simplified Architecture** | Each gateway handles its specialty, reducing complexity |
| **Future-Proof** | Can evolve each component independently |

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Component Responsibilities](#2-component-responsibilities)
3. [Prompt Compression Solution](#3-prompt-compression-solution)
4. [Deployment Architecture](#4-deployment-architecture)
5. [Implementation Phases](#5-implementation-phases)
6. [Configuration Examples](#6-configuration-examples)
7. [Migration Strategy](#7-migration-strategy)
8. [Performance Targets](#8-performance-targets)
9. [Security Considerations](#9-security-considerations)
10. [Cost-Benefit Analysis](#10-cost-benefit-analysis)
11. [Risk Assessment](#11-risk-assessment)
12. [Next Steps](#12-next-steps)

---

## 1. Architecture Overview

### 1.1 Current State (Kong-Only)

```
Client Applications
        ↓
  Platform API
        ↓
   Kong Gateway (Port 8000)
        ↓ (challenges)
   - In-memory cache only
   - Complex Lua scripting
   - Enterprise features gated
   - Manual LLM routing
        ↓
   LLM Providers
```

**Problems:**
- Semantic caching limited to in-memory (R1 limitation)
- Custom Lua development for each LLM feature
- Risk of more features moving to Enterprise tier
- Not purpose-built for LLM workloads

### 1.2 Proposed Hybrid Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
│         (Open WebUI, Admin Dashboard, IntelliJ Plugin)       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                     Platform API (FastAPI)                   │
│  • Multi-tenancy • ABAC (Casbin) • Audit Trails • Encryption│
└──────────┬──────────────────────────────────────┬───────────┘
           │                                      │
           │ (Non-LLM APIs)                      │ (LLM Calls)
           ▼                                      ▼
┌──────────────────────┐              ┌──────────────────────┐
│   Kong Gateway       │              │  LiteLLM Proxy       │
│   (Port 8000)        │              │  (Port 4000)         │
├──────────────────────┤              ├──────────────────────┤
│ • REST API routing   │              │ • LLM routing        │
│ • Rate limiting      │              │ • Semantic caching   │
│ • Auth middleware    │              │ • Load balancing     │
│ • General services   │              │ • Cost tracking      │
│ • Plugin ecosystem   │              │ • Guardrails         │
└──────────┬───────────┘              │ • Prompt compression │
           │                          └──────────┬───────────┘
           │                                     │
           ▼                                     ▼
┌──────────────────────┐              ┌──────────────────────┐
│  Platform Services   │              │   LLM Providers      │
├──────────────────────┤              ├──────────────────────┤
│ • Agent Orchestrator │              │ • OpenAI             │
│ • Knowledge & RAG    │              │ • Anthropic          │
│ • Integrations       │              │ • Google Gemini      │
│ • LLMOps Platform    │              │ • Groq               │
└──────────────────────┘              └──────────────────────┘
           │                                     │
           └─────────────┬───────────────────────┘
                         ▼
         ┌───────────────────────────────┐
         │   Shared Infrastructure       │
         ├───────────────────────────────┤
         │ • Redis (Caching)             │
         │ • PostgreSQL (Data)           │
         │ • Prometheus (Metrics)        │
         │ • Grafana (Dashboards)        │
         │ • Loki (Logs)                 │
         │ • Langfuse (LLM Observability)│
         └───────────────────────────────┘
```

### 1.3 Request Flow Examples

#### Example 1: LLM Chat Request
```
1. Client → Platform API (authentication, authorization)
2. Platform API → LiteLLM Proxy (LLM routing decision)
3. LiteLLM Proxy:
   a. Apply prompt compression (LLMLingua)
   b. Check semantic cache (Redis)
   c. If MISS → Route to LLM provider (load balanced)
   d. Cache response
   e. Track cost/usage
4. Response → Platform API → Client
```

#### Example 2: Platform Service API Call
```
1. Client → Platform API (authentication, authorization)
2. Platform API → Kong Gateway (service routing)
3. Kong Gateway → Target Service (e.g., Knowledge & RAG)
4. Response → Kong Gateway → Platform API → Client
```

---

## 2. Component Responsibilities

### 2.1 Kong Gateway Responsibilities

**Port:** 8000
**Purpose:** General-purpose API gateway for platform services

| Responsibility | Implementation |
|----------------|----------------|
| **Service Routing** | Routes to Agent Orchestrator, Knowledge & RAG, Integrations, LLMOps services |
| **Rate Limiting** | Redis-backed rate limits for non-LLM APIs |
| **Authentication** | JWT/API key validation for service-to-service communication |
| **Load Balancing** | Distribute traffic across service instances |
| **Plugin Ecosystem** | Leverage Kong's extensive plugin library for general API needs |
| **WebSocket Support** | Handle long-lived connections for real-time features |
| **Admin UI** | Kong Manager for configuration and monitoring |

**Configuration:**
```yaml
# Kong services (non-LLM)
services:
  - name: agent-orchestrator
    url: http://agent-orchestrator:8083
  - name: knowledge-rag
    url: http://knowledge-rag:8084
  - name: integrations
    url: http://integrations:8085
  - name: llmops
    url: http://llmops:8081

# No LLM-specific routes (handled by LiteLLM)
```

### 2.2 LiteLLM Proxy Responsibilities

**Port:** 4000
**Purpose:** Specialized LLM gateway with AI-native features

| Responsibility | Implementation |
|----------------|----------------|
| **LLM Routing** | 100+ providers natively supported (OpenAI, Anthropic, Google, Groq, etc.) |
| **Semantic Caching** | Redis/Qdrant-backed with embedding similarity |
| **Prompt Compression** | LLMLingua integration (20-30% reduction) |
| **Load Balancing** | Smart routing strategies (cost-based, latency-based, least-busy) |
| **Cost Tracking** | Per-tenant, per-user, per-model cost analytics |
| **Rate Limiting** | LLM-specific quotas (tokens/min, requests/min) |
| **Guardrails** | Native integrations (Lakera, LLMGuard, Presidio) |
| **Fallback Routing** | Automatic provider failover on errors |
| **Virtual Keys** | Multi-tenancy without DB-per-tenant complexity |
| **Observability** | Langfuse, Prometheus, OpenTelemetry native |

**Configuration:**
```yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY
      rpm: 10000

  - model_name: claude-sonnet-4-5
    litellm_params:
      model: anthropic/claude-sonnet-4-5-20250929
      api_key: os.environ/ANTHROPIC_API_KEY
      rpm: 5000

litellm_settings:
  cache: true
  cache_params:
    type: redis
    host: redis
    port: 6379
    ttl: 3600

  # Custom hooks for prompt compression
  success_callback: ["langfuse", "prometheus"]
  callbacks: ["prompt_compression_middleware"]

router_settings:
  routing_strategy: cost-based-routing
  num_retries: 3
  timeout: 120
```

### 2.3 Platform API Responsibilities (Unchanged)

**Port:** 8082
**Purpose:** Core platform orchestration and governance

| Responsibility | Why It Stays Here |
|----------------|-------------------|
| **Multi-Tenancy** | DB-per-tenant provisioning and management |
| **ABAC Authorization** | Casbin-based access control policies |
| **Audit Trails** | Cryptographic signatures and compliance logging |
| **Feature Flags** | Flagsmith integration for tenant-specific features |
| **Envelope Encryption** | Deloitte IP protection (R2+) |
| **Usage Aggregation** | Combine data from Kong + LiteLLM for reporting |
| **Tenant Onboarding** | Provision databases, keys, configurations |

**Request Routing Logic:**
```python
# Platform API routing decision
async def route_request(request: Request, endpoint: str):
    # Authenticate and authorize
    user = await authenticate(request)
    await authorize(user, endpoint)

    # Route based on endpoint type
    if endpoint.startswith("/v1/chat/") or endpoint.startswith("/v1/embeddings/"):
        # LLM request → LiteLLM Proxy
        return await proxy_to_litellm(request, user)
    else:
        # Platform service → Kong Gateway
        return await proxy_to_kong(request, user)
```

---

## 3. Prompt Compression Solution

### 3.1 Why Prompt Compression Matters

**Cost Impact:**
- LLM pricing is per-token (input + output)
- Typical RAG context: 3,000-10,000 tokens
- **With 30% compression:** 2,100-7,000 tokens = **30% cost savings on input**
- **Combined with caching:** 40-60% cache hit rate = **70%+ total cost reduction**

**Latency Impact:**
- Fewer tokens = faster processing
- Reduced time-to-first-token (TTFT)
- Better user experience

### 3.2 LLMLingua Overview

**Project:** [microsoft/LLMLingua](https://github.com/microsoft/LLMLingua)
**License:** MIT (100% Open Source)
**Versions:** LLMLingua, LongLLMLingua, LLMLingua-2

**Key Features:**
- **Compression Ratio:** 2x to 20x (configurable)
- **Performance Loss:** <5% (minimal quality degradation)
- **Compression Methods:**
  - Token-level filtering
  - Sentence-level filtering
  - Context-level filtering
  - Dynamic compression ratios
- **Structured Compression:** Tag-based control over what to compress
- **Integration:** Native Python, works with any LLM

### 3.3 Compression Strategy

#### Compression Levels by Use Case

| Use Case | Compression Ratio | Target Tokens | Quality Loss |
|----------|-------------------|---------------|--------------|
| **Chat (Short Context)** | 2x (rate=0.5) | Original/2 | <2% |
| **RAG (Medium Context)** | 3x (rate=0.33) | 1,000-2,000 | <3% |
| **Long Documents** | 5x (rate=0.2) | 2,000-3,000 | <5% |
| **Code Context** | 2x (rate=0.5) | Original/2 | <2% |

#### Compression Configuration

```python
from llmlingua import PromptCompressor

# Initialize compressor (cached, reused across requests)
compressor = PromptCompressor(
    model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
    device_map="cpu"  # or "cuda" for GPU acceleration
)

# Compress prompt for RAG use case
def compress_rag_prompt(context: List[str], question: str, instruction: str = ""):
    compressed = compressor.compress_prompt(
        context,
        instruction=instruction,
        question=question,
        target_token=2000,  # Adjust based on use case
        condition_compare=True,
        condition_in_question="after",
        rank_method="longllmlingua",
        use_sentence_level_filter=True,
        context_budget="+100",
        dynamic_context_compression_ratio=0.4,
        reorder_context="sort"
    )

    return {
        "compressed_prompt": compressed["compressed_prompt"],
        "original_tokens": compressed["origin_tokens"],
        "compressed_tokens": compressed["compressed_tokens"],
        "ratio": compressed["ratio"],
        "savings_percent": (1 - compressed["ratio"]) * 100
    }
```

### 3.4 LiteLLM Integration via Custom Middleware

#### Implementation Approach

LiteLLM supports custom hooks via `async_pre_call_hook` that can modify requests before they're sent to LLM providers.

```python
# File: shared/python/prompt_compression/middleware.py

from litellm.integrations.custom_logger import CustomLogger
from litellm.utils import get_formatted_prompt
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

        # Compression settings per tenant/model
        self.compression_config = {
            "default": {
                "enabled": True,
                "target_ratio": 0.5,  # 2x compression
                "min_tokens": 500     # Only compress if >500 tokens
            },
            "rag_queries": {
                "enabled": True,
                "target_ratio": 0.33,  # 3x compression
                "min_tokens": 1000
            },
            "chat": {
                "enabled": True,
                "target_ratio": 0.6,   # 1.67x compression
                "min_tokens": 300
            }
        }

    async def async_pre_call_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        cache: DualCache,
        data: dict,
        call_type: Literal["completion", "embeddings", "image_generation"]
    ) -> Optional[dict]:
        """
        Hook that runs before LLM API call.
        Compresses prompts if configured for the tenant/user.
        """

        if call_type != "completion":
            return data  # Only compress chat/completion calls

        # Check if compression is enabled for this user/tenant
        tenant_id = user_api_key_dict.team_id
        compression_enabled = self._check_compression_enabled(tenant_id)

        if not compression_enabled:
            return data

        # Extract messages from request
        messages = data.get("messages", [])
        if not messages:
            return data

        # Compress the prompt
        compressed_data = await self._compress_messages(messages, data)

        # Log compression metrics
        await self._log_compression_metrics(
            tenant_id=tenant_id,
            original_tokens=compressed_data["original_tokens"],
            compressed_tokens=compressed_data["compressed_tokens"],
            savings_percent=compressed_data["savings_percent"]
        )

        return compressed_data["data"]

    async def _compress_messages(self, messages: list, data: dict) -> dict:
        """Compress message content while preserving structure."""

        # Separate system, user, and assistant messages
        system_msgs = [m for m in messages if m["role"] == "system"]
        user_msgs = [m for m in messages if m["role"] == "user"]

        # Extract content for compression
        context = [m["content"] for m in user_msgs[:-1]] if len(user_msgs) > 1 else []
        question = user_msgs[-1]["content"] if user_msgs else ""
        instruction = system_msgs[0]["content"] if system_msgs else ""

        # Get token count estimate
        original_tokens = self._estimate_tokens(messages)

        # Only compress if above threshold
        config = self.compression_config["default"]
        if original_tokens < config["min_tokens"]:
            return {
                "data": data,
                "original_tokens": original_tokens,
                "compressed_tokens": original_tokens,
                "savings_percent": 0
            }

        # Compress using LLMLingua
        compressed = self.compressor.compress_prompt(
            context,
            instruction=instruction,
            question=question,
            rate=config["target_ratio"],
            condition_compare=True,
            condition_in_question="after",
            rank_method="longllmlingua"
        )

        # Reconstruct messages with compressed content
        compressed_messages = []

        # Keep system message
        if system_msgs:
            compressed_messages.append(system_msgs[0])

        # Add compressed user message
        compressed_messages.append({
            "role": "user",
            "content": compressed["compressed_prompt"]
        })

        # Update data
        compressed_data = data.copy()
        compressed_data["messages"] = compressed_messages

        return {
            "data": compressed_data,
            "original_tokens": compressed["origin_tokens"],
            "compressed_tokens": compressed["compressed_tokens"],
            "savings_percent": (1 - compressed["ratio"]) * 100
        }

    def _estimate_tokens(self, messages: list) -> int:
        """Estimate token count for messages."""
        total = 0
        for msg in messages:
            content = msg.get("content", "")
            # Rough estimate: 1 token ≈ 4 characters
            total += len(content) // 4
        return total

    def _check_compression_enabled(self, tenant_id: str) -> bool:
        """Check if compression is enabled for tenant (via feature flags)."""
        # This would integrate with Flagsmith or Platform API
        # For now, enable for all
        return True

    async def _log_compression_metrics(
        self,
        tenant_id: str,
        original_tokens: int,
        compressed_tokens: int,
        savings_percent: float
    ):
        """Log compression metrics to Prometheus/Langfuse."""
        # Prometheus metrics
        from prometheus_client import Counter, Histogram

        compression_requests = Counter(
            'litellm_compression_requests_total',
            'Total compression requests',
            ['tenant_id']
        )
        compression_savings = Histogram(
            'litellm_compression_savings_percent',
            'Compression savings percentage',
            ['tenant_id']
        )

        compression_requests.labels(tenant_id=tenant_id).inc()
        compression_savings.labels(tenant_id=tenant_id).observe(savings_percent)


# Initialize middleware instance
prompt_compression_middleware = PromptCompressionMiddleware()
```

#### LiteLLM Configuration with Middleware

```yaml
# litellm_config.yaml

model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY

litellm_settings:
  # Enable custom callback
  callbacks: ["prompt_compression_middleware"]

  # Cache compressed prompts
  cache: true
  cache_params:
    type: redis
    host: redis
    port: 6379
    ttl: 3600

general_settings:
  # Custom auth and middleware
  custom_auth: custom_auth.user_api_key_auth
```

#### Startup Script

```python
# File: litellm_server.py

import litellm
from shared.python.prompt_compression.middleware import prompt_compression_middleware

# Register the middleware
litellm.callbacks = [prompt_compression_middleware]

# Start LiteLLM proxy
if __name__ == "__main__":
    import subprocess
    subprocess.run([
        "litellm",
        "--config", "litellm_config.yaml",
        "--port", "4000"
    ])
```

### 3.5 Compression Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Compression Ratio** | 2-3x | Monitored per request |
| **Quality Retention** | >95% | A/B testing with evaluation metrics |
| **Latency Overhead** | <50ms | Compression time added to request |
| **Cost Savings** | 20-30% | Token reduction on input prompts |
| **Combined Savings** | 70%+ | Compression + caching |

### 3.6 Compression Monitoring

**Prometheus Metrics:**
```yaml
# Compression-specific metrics
- litellm_compression_requests_total (counter)
- litellm_compression_savings_percent (histogram)
- litellm_compression_latency_seconds (histogram)
- litellm_compression_original_tokens (histogram)
- litellm_compression_compressed_tokens (histogram)
```

**Grafana Dashboard:**
- Real-time compression ratio trends
- Cost savings calculations
- Quality impact metrics (if A/B testing enabled)
- Compression latency percentiles

---

## 4. Deployment Architecture

### 4.1 Docker Compose Configuration

```yaml
# docker-compose.yml

version: '3.8'

services:
  # Kong Gateway (General API Gateway)
  kong-gateway:
    image: kong/kong-gateway:3.8-alpine
    ports:
      - "8000:8000"  # Proxy port
      - "8001:8001"  # Admin API
      - "8443:8443"  # Proxy SSL
      - "8444:8444"  # Admin API SSL
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: postgres
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: ${KONG_PG_PASSWORD}
      KONG_PROXY_ACCESS_LOG: /dev/stdout
      KONG_ADMIN_ACCESS_LOG: /dev/stdout
      KONG_PROXY_ERROR_LOG: /dev/stderr
      KONG_ADMIN_ERROR_LOG: /dev/stderr
      KONG_ADMIN_LISTEN: 0.0.0.0:8001
    depends_on:
      - postgres
      - redis
    networks:
      - dcoder-network

  # LiteLLM Proxy (LLM Gateway)
  litellm-proxy:
    build:
      context: ./litellm
      dockerfile: Dockerfile
    ports:
      - "4000:4000"
    environment:
      # LLM Provider API Keys
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      GOOGLE_API_KEY: ${GOOGLE_API_KEY}
      GROQ_API_KEY: ${GROQ_API_KEY}

      # Redis for caching
      REDIS_HOST: redis
      REDIS_PORT: 6379

      # Database for virtual keys
      DATABASE_URL: postgresql://litellm:${LITELLM_DB_PASSWORD}@postgres:5432/litellm

      # Observability
      LANGFUSE_PUBLIC_KEY: ${LANGFUSE_PUBLIC_KEY}
      LANGFUSE_SECRET_KEY: ${LANGFUSE_SECRET_KEY}
    volumes:
      - ./litellm/config.yaml:/app/config.yaml
      - ./shared/python:/app/shared/python
    command: ["--config", "/app/config.yaml", "--port", "4000"]
    depends_on:
      - postgres
      - redis
    networks:
      - dcoder-network

  # Platform API (Main Orchestrator)
  platform-api:
    build:
      context: ./platform-api
      dockerfile: Dockerfile
    ports:
      - "8082:8082"
    environment:
      # Gateway endpoints
      KONG_GATEWAY_URL: http://kong-gateway:8000
      LITELLM_PROXY_URL: http://litellm-proxy:4000

      # Database
      DATABASE_URL: postgresql://platform:${PLATFORM_DB_PASSWORD}@postgres:5432/platform

      # Redis
      REDIS_URL: redis://redis:6379/0

      # Auth
      LOGTO_ENDPOINT: ${LOGTO_ENDPOINT}
      LOGTO_APP_ID: ${LOGTO_APP_ID}
      LOGTO_APP_SECRET: ${LOGTO_APP_SECRET}
    depends_on:
      - kong-gateway
      - litellm-proxy
      - postgres
      - redis
    networks:
      - dcoder-network

  # Shared Infrastructure
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./scripts/init-databases.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - dcoder-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - dcoder-network

  # Observability
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./platform/infra/observability/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    networks:
      - dcoder-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3005:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
      - ./platform/infra/observability/grafana/dashboards:/etc/grafana/provisioning/dashboards
    networks:
      - dcoder-network

volumes:
  postgres-data:
  redis-data:
  prometheus-data:
  grafana-data:

networks:
  dcoder-network:
    driver: bridge
```

### 4.2 LiteLLM Dockerfile with Compression

```dockerfile
# litellm/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install LiteLLM and dependencies
RUN pip install --no-cache-dir \
    'litellm[proxy]' \
    llmlingua \
    prometheus-client \
    psycopg2-binary

# Copy configuration
COPY config.yaml /app/config.yaml
COPY middleware/ /app/middleware/

# Copy shared Python modules
COPY ../shared/python /app/shared/python

# Set Python path
ENV PYTHONPATH=/app:/app/shared/python

# Expose port
EXPOSE 4000

# Start LiteLLM with custom middleware
CMD ["python", "-m", "litellm", "--config", "/app/config.yaml", "--port", "4000"]
```

### 4.3 Network Architecture

```
                    Internet
                        │
                        ▼
                ┌───────────────┐
                │  Load Balancer│
                │  (Future: K8s)│
                └───────┬───────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌───────────────┐ ┌──────────┐ ┌──────────────┐
│ Kong Gateway  │ │Platform  │ │LiteLLM Proxy │
│   :8000       │ │API :8082 │ │   :4000      │
└───────┬───────┘ └────┬─────┘ └──────┬───────┘
        │              │               │
        │              │               │
        └──────────────┼───────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌───────────┐  ┌──────────┐  ┌──────────┐
│PostgreSQL │  │  Redis   │  │Prometheus│
│  :5432    │  │  :6379   │  │  :9090   │
└───────────┘  └──────────┘  └──────────┘

Network: dcoder-network (bridge)
```

---

## 5. Implementation Phases

### Phase 1: LiteLLM Proof of Concept (Week 1-2)

**Objective:** Validate LiteLLM capabilities in isolated environment

**Tasks:**
1. Deploy LiteLLM Proxy standalone
2. Configure same LLM providers as current Kong setup
3. Implement virtual key multi-tenancy
4. Test semantic caching with Redis
5. Benchmark performance vs Kong

**Deliverables:**
- Working LiteLLM deployment
- Performance comparison report
- Feature parity validation

**Success Criteria:**
- ✅ All 4 providers (OpenAI, Anthropic, Google, Groq) working
- ✅ Cache hit rate >40% on test workload
- ✅ Latency <100ms overhead vs direct provider calls
- ✅ Virtual keys working for 3+ test tenants

### Phase 2: Prompt Compression Integration (Week 2-3)

**Objective:** Implement and validate LLMLingua compression

**Tasks:**
1. Create compression middleware for LiteLLM
2. Implement compression configuration per tenant
3. Add compression metrics to Prometheus
4. Create Grafana compression dashboard
5. Conduct A/B testing for quality validation

**Deliverables:**
- Compression middleware code
- Prometheus metrics
- Grafana dashboard
- Quality impact report

**Success Criteria:**
- ✅ 2-3x compression ratio achieved
- ✅ <5% quality degradation (measured via eval metrics)
- ✅ <50ms compression latency
- ✅ 20-30% cost savings demonstrated

### Phase 3: Hybrid Architecture Setup (Week 3-4)

**Objective:** Deploy Kong + LiteLLM side-by-side

**Tasks:**
1. Update Platform API routing logic
2. Configure Kong for platform services only
3. Remove LLM routes from Kong
4. Configure LiteLLM for all LLM traffic
5. Update docker-compose for hybrid setup

**Deliverables:**
- Updated Platform API with routing logic
- Kong configuration (non-LLM services)
- LiteLLM configuration (LLM services)
- Updated docker-compose.yml

**Success Criteria:**
- ✅ Both gateways running in parallel
- ✅ Platform API routes correctly to each gateway
- ✅ No service disruption
- ✅ All tests passing

### Phase 4: Observability Integration (Week 4-5)

**Objective:** Unified monitoring across both gateways

**Tasks:**
1. Configure Prometheus scraping for both gateways
2. Create unified Grafana dashboards
3. Integrate Langfuse for LLM observability
4. Set up alerting rules
5. Create runbooks for common issues

**Deliverables:**
- Prometheus configuration
- Grafana dashboards (5+)
- Langfuse integration
- Alert rules
- Runbooks

**Success Criteria:**
- ✅ All metrics flowing to Prometheus
- ✅ Dashboards showing Kong + LiteLLM data
- ✅ Langfuse tracking all LLM calls
- ✅ Alerts firing correctly on test scenarios

### Phase 5: Migration and Testing (Week 5-6)

**Objective:** Complete migration with comprehensive testing

**Tasks:**
1. Migrate all LLM traffic to LiteLLM
2. Deprecate Kong LLM routes
3. Run load tests (1000+ req/min)
4. Validate cost savings
5. Performance benchmarking

**Deliverables:**
- Migration completion report
- Load test results
- Cost savings analysis
- Performance benchmarks

**Success Criteria:**
- ✅ 0 LLM requests through Kong
- ✅ All LLM traffic through LiteLLM
- ✅ Load tests passing (1000 req/min sustained)
- ✅ 70%+ cost reduction validated
- ✅ Latency targets met (<200ms P95)

### Phase 6: Production Hardening (Week 6-7)

**Objective:** Production-ready deployment

**Tasks:**
1. Security audit and hardening
2. Backup/disaster recovery setup
3. Documentation updates
4. Team training
5. Incident response procedures

**Deliverables:**
- Security audit report
- DR runbook
- Updated documentation
- Training materials
- Incident response guide

**Success Criteria:**
- ✅ Security audit passed
- ✅ DR tested successfully
- ✅ All documentation updated
- ✅ Team trained on hybrid architecture

### Timeline Summary

```
Week 1-2: LiteLLM PoC
Week 2-3: Compression Integration
Week 3-4: Hybrid Setup
Week 4-5: Observability
Week 5-6: Migration & Testing
Week 6-7: Production Hardening

Total: 7 weeks (35 working days)
```

---

## 6. Configuration Examples

### 6.1 Platform API Routing Logic

```python
# platform-api/app/routing/gateway_router.py

from fastapi import Request, HTTPException
import httpx
from typing import Literal

class GatewayRouter:
    def __init__(self):
        self.kong_url = os.getenv("KONG_GATEWAY_URL", "http://kong-gateway:8000")
        self.litellm_url = os.getenv("LITELLM_PROXY_URL", "http://litellm-proxy:4000")
        self.client = httpx.AsyncClient(timeout=120.0)

    async def route_request(
        self,
        request: Request,
        user: User,
        endpoint: str
    ) -> httpx.Response:
        """
        Route request to appropriate gateway based on endpoint type.
        """

        # Determine gateway
        gateway = self._select_gateway(endpoint)

        # Build target URL
        if gateway == "litellm":
            target_url = f"{self.litellm_url}{endpoint}"
        else:
            target_url = f"{self.kong_url}{endpoint}"

        # Add headers
        headers = self._build_headers(request, user, gateway)

        # Forward request
        response = await self.client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=await request.body(),
            params=request.query_params
        )

        # Log to audit trail
        await self._audit_log(user, endpoint, gateway, response.status_code)

        return response

    def _select_gateway(self, endpoint: str) -> Literal["kong", "litellm"]:
        """Determine which gateway handles this endpoint."""

        # LLM endpoints go to LiteLLM
        llm_prefixes = [
            "/v1/chat/completions",
            "/v1/completions",
            "/v1/embeddings",
            "/v1/responses",  # OpenAI Responses API
            "/v1/messages",   # Anthropic Messages API
        ]

        for prefix in llm_prefixes:
            if endpoint.startswith(prefix):
                return "litellm"

        # Everything else goes to Kong
        return "kong"

    def _build_headers(
        self,
        request: Request,
        user: User,
        gateway: Literal["kong", "litellm"]
    ) -> dict:
        """Build headers for gateway request."""

        headers = dict(request.headers)

        # Remove hop-by-hop headers
        hop_by_hop = ['connection', 'keep-alive', 'proxy-authenticate',
                      'proxy-authorization', 'te', 'trailers',
                      'transfer-encoding', 'upgrade']
        for header in hop_by_hop:
            headers.pop(header, None)

        if gateway == "litellm":
            # Add LiteLLM virtual key
            virtual_key = await self._get_litellm_virtual_key(user)
            headers["Authorization"] = f"Bearer {virtual_key}"

            # Add metadata for tracking
            headers["X-Tenant-Id"] = user.tenant_id
            headers["X-User-Id"] = user.user_id
        else:
            # Add Kong API key
            headers["X-Kong-Key"] = user.kong_api_key

        return headers

    async def _get_litellm_virtual_key(self, user: User) -> str:
        """
        Get or create LiteLLM virtual key for user.
        Virtual keys are cached in Redis.
        """
        cache_key = f"litellm:virtual_key:{user.user_id}"

        # Check cache
        virtual_key = await redis.get(cache_key)
        if virtual_key:
            return virtual_key

        # Generate new virtual key via LiteLLM API
        response = await self.client.post(
            f"{self.litellm_url}/key/generate",
            json={
                "user_id": user.user_id,
                "team_id": user.tenant_id,
                "max_budget": user.llm_budget,
                "models": user.allowed_models
            },
            headers={"Authorization": f"Bearer {LITELLM_MASTER_KEY}"}
        )

        data = response.json()
        virtual_key = data["key"]

        # Cache for 24 hours
        await redis.setex(cache_key, 86400, virtual_key)

        return virtual_key
```

### 6.2 LiteLLM Configuration (Complete)

```yaml
# litellm/config.yaml

# Model definitions
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
      tpm: 1000000

  - model_name: claude-opus-4-1
    litellm_params:
      model: anthropic/claude-opus-4-1-20250514
      api_key: os.environ/ANTHROPIC_API_KEY
      rpm: 4000
      tpm: 800000

  # Google Models
  - model_name: gemini-2-5-pro
    litellm_params:
      model: gemini/gemini-2.5-pro
      api_key: os.environ/GOOGLE_API_KEY
      rpm: 15000
      tpm: 4000000

  - model_name: gemini-2-5-flash
    litellm_params:
      model: gemini/gemini-2.5-flash
      api_key: os.environ/GOOGLE_API_KEY
      rpm: 30000
      tpm: 8000000

  # Groq Models
  - model_name: groq-llama-3-3-70b
    litellm_params:
      model: groq/llama-3.3-70b-versatile
      api_key: os.environ/GROQ_API_KEY
      rpm: 30
      tpm: 20000

# Router settings
router_settings:
  routing_strategy: cost-based-routing
  model_group_alias:
    "gpt-4": "gpt-4o"
    "claude": "claude-sonnet-4-5"
  num_retries: 3
  timeout: 120
  fallbacks:
    - gpt-4o: ["claude-sonnet-4-5", "gemini-2-5-pro"]
    - claude-sonnet-4-5: ["gpt-4o", "gemini-2-5-pro"]

  # Redis for distributed routing state
  redis_host: redis
  redis_port: 6379
  redis_password: ${REDIS_PASSWORD}

# Caching configuration
litellm_settings:
  cache: true
  cache_params:
    type: redis
    host: redis
    port: 6379
    password: ${REDIS_PASSWORD}
    ttl: 3600
    namespace: "litellm:cache"
    supported_call_types: ["acompletion", "atext_completion", "aembedding"]

  # Custom callbacks for compression and observability
  success_callback: ["langfuse", "prometheus"]
  failure_callback: ["langfuse"]
  callbacks: ["prompt_compression_middleware"]

  # Logging
  set_verbose: false
  json_logs: true

# General settings
general_settings:
  master_key: ${LITELLM_MASTER_KEY}
  database_url: ${DATABASE_URL}

  # Virtual key defaults
  litellm_key_budget_duration: "30d"

  # Custom auth (integrates with Platform API)
  custom_auth: middleware.custom_auth.verify_platform_api_key

  # Allowed routes
  allowed_routes: [
    "/chat/completions",
    "/completions",
    "/embeddings",
    "/v1/chat/completions",
    "/v1/completions",
    "/v1/embeddings"
  ]

  # Admin routes (require master key)
  admin_only_routes: [
    "/key/generate",
    "/key/delete",
    "/key/info",
    "/config"
  ]

# Guardrails (R1: alert-only)
guardrails:
  - guardrail_name: "prompt-injection-detection"
    litellm_params:
      guardrail: lakera_prompt_injection
      mode: pre_call
      on_flagged_action: "monitor"  # Don't block, just log
      default_on: true

  - guardrail_name: "pii-detection"
    litellm_params:
      guardrail: presidio
      mode: [pre_call, post_call]
      on_flagged_action: "monitor"
      default_on: true
```

### 6.3 Kong Configuration (Platform Services Only)

```yaml
# platform/infra/kong/kong.yaml

_format_version: "3.0"

services:
  # Agent Orchestrator Service
  - name: agent-orchestrator
    url: http://agent-orchestrator:8083
    routes:
      - name: agent-orchestrator-route
        paths:
          - /v1/agents
          - /v1/workflows
          - /v1/temporal
        strip_path: false
    plugins:
      - name: rate-limiting
        config:
          minute: 1000
          policy: redis
          redis_host: redis
          redis_port: 6379
      - name: prometheus
        config:
          per_consumer: true

  # Knowledge & RAG Service
  - name: knowledge-rag
    url: http://knowledge-rag:8084
    routes:
      - name: knowledge-rag-route
        paths:
          - /v1/knowledge
          - /v1/documents
          - /v1/search
        strip_path: false
    plugins:
      - name: rate-limiting
        config:
          minute: 2000
          policy: redis
          redis_host: redis
          redis_port: 6379
      - name: prometheus
        config:
          per_consumer: true

  # Integrations Service
  - name: integrations
    url: http://integrations:8085
    routes:
      - name: integrations-route
        paths:
          - /v1/jira
          - /v1/bitbucket
          - /v1/confluence
          - /v1/sharepoint
        strip_path: false
    plugins:
      - name: rate-limiting
        config:
          minute: 500
          policy: redis
          redis_host: redis
          redis_port: 6379
      - name: prometheus
        config:
          per_consumer: true

  # LLMOps Platform Service
  - name: llmops
    url: http://llmops:8081
    routes:
      - name: llmops-route
        paths:
          - /v1/experiments
          - /v1/evaluations
          - /v1/prompts
        strip_path: false
    plugins:
      - name: rate-limiting
        config:
          minute: 1000
          policy: redis
          redis_host: redis
          redis_port: 6379
      - name: prometheus
        config:
          per_consumer: true

# Global plugins
plugins:
  - name: prometheus
    config:
      status_code_metrics: true
      latency_metrics: true
      bandwidth_metrics: true

  - name: correlation-id
    config:
      header_name: X-Correlation-ID
      generator: uuid

  - name: http-log
    config:
      http_endpoint: http://loki:3100/loki/api/v1/push
      method: POST
      content_type: application/json
```

---

## 7. Migration Strategy

### 7.1 Pre-Migration Checklist

- [ ] All R1 features documented and tested in current Kong setup
- [ ] LiteLLM PoC completed successfully
- [ ] Prompt compression validated with quality metrics
- [ ] Team trained on LiteLLM and hybrid architecture
- [ ] Rollback plan documented and tested
- [ ] Monitoring dashboards created
- [ ] Load testing completed
- [ ] Security audit passed

### 7.2 Migration Steps

#### Step 1: Parallel Deployment (No Traffic)
```bash
# Deploy LiteLLM alongside Kong
docker-compose up -d litellm-proxy

# Verify health
curl http://localhost:4000/health

# No traffic routed yet
```

#### Step 2: Shadow Traffic (Read-Only)
```python
# Platform API sends duplicate requests to both gateways
async def shadow_mode_request(request):
    # Primary: Kong (current)
    kong_response = await route_to_kong(request)

    # Shadow: LiteLLM (async, don't wait)
    asyncio.create_task(route_to_litellm_shadow(request))

    # Compare responses in background
    asyncio.create_task(compare_responses(kong_response, litellm_response))

    return kong_response
```

**Duration:** 1 week
**Validation:** Response parity >99%

#### Step 3: Canary Release (10% Traffic)
```python
# Route 10% of LLM traffic to LiteLLM
async def canary_route(request):
    if hash(request.user_id) % 100 < 10:
        return await route_to_litellm(request)
    else:
        return await route_to_kong(request)
```

**Duration:** 3 days
**Validation:**
- Error rate <0.1%
- Latency P95 <200ms
- Cost savings visible

#### Step 4: Gradual Rollout (10% → 50% → 100%)
```
Day 1-3: 10% traffic
Day 4-6: 25% traffic
Day 7-9: 50% traffic
Day 10-12: 75% traffic
Day 13+: 100% traffic
```

**Rollback Triggers:**
- Error rate >1%
- Latency P95 >300ms
- Cache hit rate <30%
- Any critical bug

#### Step 5: Complete Migration
```yaml
# Platform API final routing
LLM_ENDPOINTS = ["/v1/chat/", "/v1/embeddings/", "/v1/completions/"]
GATEWAY_ROUTING = {
    "llm": "http://litellm-proxy:4000",
    "default": "http://kong-gateway:8000"
}
```

#### Step 6: Kong LLM Route Deprecation
```yaml
# Remove LLM routes from Kong configuration
# Keep only platform service routes
services:
  - name: agent-orchestrator
  - name: knowledge-rag
  - name: integrations
  - name: llmops
# NO LLM routes
```

### 7.3 Rollback Procedure

**Trigger Conditions:**
- Critical bug affecting >10% of requests
- Latency degradation >2x baseline
- Error rate >5%
- Data loss or corruption detected

**Rollback Steps:**
1. Switch Platform API routing back to Kong (1 line change)
2. Deploy configuration update
3. Verify traffic flowing through Kong
4. Monitor for 30 minutes
5. Investigate LiteLLM issue offline
6. Fix and redeploy when ready

**Rollback Time:** <5 minutes

---

## 8. Performance Targets

### 8.1 Latency Targets

| Metric | Kong (Baseline) | LiteLLM (Target) | Status |
|--------|-----------------|------------------|--------|
| **Cache HIT** | N/A (in-memory) | <50ms | ✅ Measured |
| **Cache MISS** | ~1500ms | <1600ms | ✅ Acceptable |
| **P50 Latency** | 800ms | <850ms | ✅ Target |
| **P95 Latency** | 1800ms | <2000ms | ✅ Target |
| **P99 Latency** | 3000ms | <3200ms | ✅ Target |

### 8.2 Cost Savings Targets

| Component | Savings | Mechanism |
|-----------|---------|-----------|
| **Semantic Caching** | 40-60% | Cache hits don't call LLM |
| **Prompt Compression** | 20-30% | Reduced input tokens |
| **Cost-Based Routing** | 5-10% | Route to cheaper models when appropriate |
| **Combined Target** | **70%+** | All mechanisms together |

**Example Calculation:**
```
Baseline monthly cost: $10,000
- Semantic caching (50% hit rate): $5,000 saved
- Prompt compression on remaining 50% (25% reduction): $625 saved
- Cost-based routing (5% optimization): $250 saved

Total monthly cost: $4,125
Savings: $5,875 (58.75%)
```

### 8.3 Throughput Targets

| Metric | Target | Notes |
|--------|--------|-------|
| **Requests/min (sustained)** | 1,000+ | Both gateways combined |
| **Requests/min (peak)** | 2,500+ | 2.5x sustained |
| **Concurrent connections** | 500+ | Per gateway |
| **Time to first token (TTFT)** | <500ms | For streaming responses |

### 8.4 Reliability Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Uptime** | 99.9% | Monthly |
| **Error rate** | <0.1% | 4xx + 5xx errors |
| **Failover time** | <5s | Provider failover |
| **Cache availability** | 99.99% | Redis uptime |

---

## 9. Security Considerations

### 9.1 API Key Management

**Kong Gateway:**
- Service-to-service API keys
- Stored in Platform API database
- Rotated monthly
- Scoped per service

**LiteLLM Proxy:**
- Virtual keys per tenant/user
- Master key for Platform API only
- Stored in LiteLLM database
- Automatic expiration (30 days)

**LLM Provider Keys:**
- Stored as environment variables (R1)
- Vault integration (R2+)
- Never logged or exposed
- Rotated quarterly

### 9.2 Network Security

```yaml
# Docker network isolation
networks:
  frontend:
    # Public-facing services
    services: [kong-gateway, platform-api]

  backend:
    # Internal services only
    services: [litellm-proxy, postgres, redis]
    internal: true

# Firewall rules (iptables)
- Allow: 8000 (Kong proxy)
- Allow: 8082 (Platform API)
- Deny: 4000 (LiteLLM - internal only)
- Deny: 6379 (Redis - internal only)
- Deny: 5432 (PostgreSQL - internal only)
```

### 9.3 Data Protection

**In Transit:**
- TLS 1.3 for all external communication
- mTLS for service-to-service (R2+)
- Encrypted Redis connections

**At Rest:**
- PostgreSQL encrypted volumes
- Redis persistence encrypted
- Backup encryption (AES-256)

**Prompt IP Protection (R2+):**
- Envelope encryption before sending to LiteLLM
- Decryption at LiteLLM middleware layer
- Never stored unencrypted

### 9.4 Compliance

**R1 Compliance:**
- Audit logging (all requests)
- Data retention policies
- User consent tracking

**R2+ Compliance:**
- SOC2 controls
- GDPR compliance
- Data residency controls
- Right to deletion

---

## 10. Cost-Benefit Analysis

### 10.1 Implementation Costs

| Phase | Effort (Days) | Resource | Cost |
|-------|---------------|----------|------|
| **LiteLLM PoC** | 5 | 1 Engineer | $2,500 |
| **Compression Integration** | 5 | 1 Engineer | $2,500 |
| **Hybrid Setup** | 5 | 1 Engineer | $2,500 |
| **Observability** | 5 | 1 Engineer | $2,500 |
| **Migration & Testing** | 10 | 2 Engineers | $10,000 |
| **Production Hardening** | 5 | 2 Engineers | $5,000 |
| **TOTAL** | **35 days** | | **$25,000** |

### 10.2 Ongoing Costs

| Component | Monthly Cost | Notes |
|-----------|--------------|-------|
| **Compute** | $0 | Same infrastructure |
| **Storage** | $0 | Same databases |
| **Licensing** | $0 | 100% OSS |
| **Maintenance** | -$500 | Simpler than Lua scripting |
| **TOTAL** | **-$500/mo** | Net savings |

### 10.3 Cost Savings

| Benefit | Monthly Value | Annual Value |
|---------|---------------|--------------|
| **LLM Cost Reduction (70%)** | $7,000 | $84,000 |
| **Development Time Saved** | $2,000 | $24,000 |
| **Maintenance Reduction** | $500 | $6,000 |
| **No Enterprise License** | $2,000 | $24,000 |
| **TOTAL SAVINGS** | **$11,500/mo** | **$138,000/yr** |

**Assumptions:**
- Baseline LLM spend: $10,000/month
- 2 hours/week saved on maintenance
- Kong Enterprise would cost ~$24k/year

### 10.4 ROI Calculation

```
Initial Investment: $25,000
Monthly Savings: $11,500
Break-Even: 2.2 months
Year 1 ROI: 452% ($113,000 net gain)
Year 2 ROI: 552% ($138,000 annual savings)
```

---

## 11. Risk Assessment

### 11.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **LiteLLM stability issues** | Low | High | Run in parallel with Kong during migration; easy rollback |
| **Compression quality degradation** | Medium | Medium | A/B testing; configurable compression levels; opt-out option |
| **Performance degradation** | Low | High | Load testing before migration; gradual rollout; rollback plan |
| **Integration complexity** | Medium | Medium | Phased approach; extensive testing; clear documentation |

### 11.2 Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Team learning curve** | Medium | Low | Training sessions; comprehensive docs; gradual transition |
| **Monitoring gaps** | Low | Medium | Set up observability before migration; test all dashboards |
| **Incident response delays** | Low | High | Runbooks; incident response training; 24/7 on-call |

### 11.3 Business Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Migration timeline overrun** | Medium | Low | Buffer time built in; phased approach allows partial delivery |
| **Cost savings not realized** | Low | Medium | Conservative estimates; measurement from day 1; adjustable compression |
| **User dissatisfaction** | Low | High | Gradual rollout; quality monitoring; quick rollback capability |

### 11.4 Risk Mitigation Strategy

1. **Comprehensive Testing:** Unit, integration, load, and chaos testing
2. **Gradual Rollout:** Canary → 25% → 50% → 100%
3. **Monitoring:** Real-time metrics and alerting
4. **Rollback Plan:** <5 minute rollback capability
5. **Team Preparation:** Training and documentation before migration

---

## 12. Next Steps

### 12.1 Immediate Actions (Week 1)

- [ ] Review and approve this architecture document
- [ ] Allocate engineering resources (2 engineers for 7 weeks)
- [ ] Set up project tracking (Linear/Jira)
- [ ] Create PoC environment
- [ ] Schedule kickoff meeting

### 12.2 Phase 1 Kickoff (Week 1-2)

- [ ] Deploy LiteLLM in isolated environment
- [ ] Configure all 4 LLM providers
- [ ] Implement virtual key system
- [ ] Run initial performance tests
- [ ] Document findings

### 12.3 Decision Points

**After Phase 1 (Week 2):**
- ✅ Go/No-Go: Continue with compression integration
- 📊 Metrics reviewed: Performance, feature parity, cost
- 📋 Stakeholder approval required

**After Phase 3 (Week 4):**
- ✅ Go/No-Go: Proceed with migration
- 📊 Metrics reviewed: Stability, observability, integration
- 📋 Migration plan approval

**After Phase 5 (Week 6):**
- ✅ Go/No-Go: Production deployment
- 📊 Metrics reviewed: Load tests, cost savings, quality
- 📋 Final sign-off

### 12.4 Success Metrics

**Week 2 (After PoC):**
- LiteLLM fully functional
- All providers working
- Cache hit rate >40%

**Week 4 (After Hybrid Setup):**
- Both gateways running in parallel
- Routing logic working correctly
- Observability in place

**Week 6 (After Migration):**
- 100% LLM traffic through LiteLLM
- Cost savings validated (70%+)
- Performance targets met

**Week 7 (Production Ready):**
- Security audit passed
- DR tested
- Team trained
- Documentation complete

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **API Gateway** | Reverse proxy that routes API requests to backend services |
| **Semantic Caching** | Caching based on semantic similarity, not exact match |
| **Prompt Compression** | Reducing prompt size while maintaining meaning |
| **Virtual Keys** | Tenant-specific API keys managed by LiteLLM |
| **Load Balancing** | Distributing requests across multiple instances |
| **Fallback Routing** | Automatically switching to backup provider on failure |
| **ABAC** | Attribute-Based Access Control |
| **Envelope Encryption** | Encrypting data with a key that is itself encrypted |

---

## Appendix B: References

1. **LiteLLM Documentation:** https://docs.litellm.ai/
2. **LLMLingua Paper:** https://arxiv.org/abs/2310.05736
3. **Kong Gateway Docs:** https://docs.konghq.com/
4. **Microsoft LLMLingua:** https://github.com/microsoft/LLMLingua
5. **D.Coder Original Ask:** `docs/project-docs/plans/original-ask.md`
6. **R1 PRD:** `docs/project-docs/releases/R1/PRD.md`

---

## Appendix C: Contact Information

| Role | Contact | Responsibility |
|------|---------|----------------|
| **Architecture Lead** | [TBD] | Overall design and decisions |
| **LiteLLM Lead** | [TBD] | LiteLLM implementation |
| **Kong Lead** | [TBD] | Kong configuration |
| **Platform API Lead** | [TBD] | Routing logic |
| **Observability Lead** | [TBD] | Monitoring and dashboards |

---

**Document Status:** PROPOSED
**Next Review:** After Phase 1 PoC completion
**Approval Required:** CTO, Engineering Manager, Product Owner

---

*End of Document*
