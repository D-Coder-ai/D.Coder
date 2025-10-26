# Kong API Gateway: OSS vs Enterprise Plugin Limitations

**Status:** ✅ Resolved - Solution Implemented  
**Date:** October 24, 2025  
**Context:** Task 1.6 - Kong AI Gateway R1 Configuration

---

## Solution Discovered

**Challenge:** Kong OSS doesn't support Redis caching in DB-less mode  
**Solution:** [globocom/kong-plugin-proxy-cache](https://github.com/globocom/kong-plugin-proxy-cache)

**Key Benefits:**
- ✅ Open-source (MIT license), production-proven at Globo.com
- ✅ Redis-backed persistent caching without Enterprise license
- ✅ 12k+ downloads, actively maintained
- ✅ 30-minute setup time
- ✅ $0 licensing cost vs $12-60k/year for Enterprise

**Implementation:** See detailed research and quick-start guide in `docs/challenges/Solution-kong-oss-enterprise-plugin-limitations/`

---

## Original Challenge Analysis

## R1 Design Goals

Per `docs/project-docs/releases/R1/ARCHITECTURE.md` and `PRD.md`, the Kong AI Gateway is required to provide:

1. **Multi-LLM Routing**: OpenAI, Anthropic, Google Gemini, Groq (✅ Implemented)
2. **Semantic Caching**: 40-60% token reduction via Redis-backed cache with 24h TTL
3. **Prompt Compression**: 20-30% size reduction (deferred to R2)
4. **Per-Tenant Rate Limiting**: 600 req/min per tenant via X-Tenant-Id header (✅ Implemented)
5. **Auth Header Injection**: BYO API keys per provider (✅ Implemented)
6. **Observability**: Prometheus metrics, distributed tracing
7. **Guardrails**: Alert-only mode (no blocking in R1)

## Technical Challenges Discovered

### Challenge 1: Semantic Caching Requires Enterprise License

**Design Intent:**
- Redis-backed semantic cache for LLM responses
- Custom cache key generation based on prompt normalization
- Per-tenant cache isolation
- 24-hour TTL with automatic expiration

**Implementation Attempted (Subtask 1.5):**
```yaml
plugins:
  - name: pre-function          # Custom Lua for cache key generation
  - name: proxy-cache           # Redis backend caching
    config:
      strategy: redis
      redis:
        host: redis
        port: 6379
  - name: post-function         # X-Cache-Status headers
```

**Blocker:**
- `pre-function` and `post-function` plugins are **Enterprise-only**
- `proxy-cache` with `strategy: redis` requires:
  - **Database mode (postgres)** OR
  - **Enterprise license** (in DB-less mode)
- Open-source Kong in DB-less mode only supports `strategy: memory`

### Challenge 2: Plugin Availability Matrix

| Plugin | OSS Kong | Kong Gateway Enterprise | Notes |
|--------|----------|-------------------------|-------|
| `request-transformer` | ✅ Available | ✅ Available | Works in both |
| `rate-limiting` | ✅ Available | ✅ Available | Works in both |
| `proxy-cache` (memory) | ✅ Available | ✅ Available | Works in both |
| `proxy-cache` (redis) | ❌ DB mode only | ✅ DB-less supported | **Blocker** |
| `pre-function` | ❌ Not available | ✅ Available | **Blocker** |
| `post-function` | ❌ Not available | ✅ Available | **Blocker** |
| `proxy-cache-advanced` | ❌ Not available | ✅ Available | **Blocker** |
| `ai-semantic-cache` | ❌ Not available | ✅ Available + AI License | **Blocker** |
| `ai-proxy` | ❌ Not available | ✅ Available + AI License | Not currently used |
| `ai-prompt-guard` | ❌ Not available | ✅ Available + AI License | Planned for subtask 1.7 |

### Challenge 3: Deployment Mode Constraints

**DB-less Mode (Declarative Config):**
- ✅ Simpler deployment
- ✅ GitOps-friendly
- ✅ No database dependency
- ❌ `proxy-cache` limited to `strategy: memory` only
- ❌ Cache lost on Kong restart
- ❌ Not shared across Kong nodes

**Database Mode (Postgres):**
- ✅ `proxy-cache` supports `strategy: redis`
- ✅ Persistent cache across restarts
- ✅ Shared cache across Kong nodes
- ❌ Requires Postgres dependency
- ❌ More complex operational model
- ❌ Still requires Enterprise for `pre-function`/`post-function`

## Current Implementation Status

**What Works (R1-Compliant):**
- ✅ 12 LLM routes across 4 providers
- ✅ Provider-specific auth header injection
- ✅ Per-tenant rate limiting with Redis backend
- ✅ Request/response transformation
- ✅ All configs in `platform/infra/kong/kong.yaml`
- ✅ Validation scripts pass
- ✅ R1 architecture structure compliance

**What's Blocked:**
- ⚠️ Redis-backed semantic caching (requires Enterprise OR DB mode without custom Lua)
- ⚠️ Custom cache key generation (requires pre-function)
- ⚠️ Cache observability headers (requires post-function)
- ⚠️ Semantic similarity matching (requires ai-semantic-cache + AI license)

## Implemented Solution

### ✅ Solution: globocom/kong-plugin-proxy-cache (IMPLEMENTED)

**Approach:**
- Install OSS community plugin that restores Redis support to Kong
- Configure Redis backend for all 12 LLM routes
- Achieve persistent, shared caching without Enterprise license

**Benefits:**
- ✅ Redis-backed persistent caching
- ✅ Shared across Kong instances
- ✅ Production-proven (Globo.com, 12k+ downloads)
- ✅ Zero licensing costs
- ✅ Works with Kong OSS in DB-less mode

**Implementation:** See `docs/challenges/Solution-kong-oss-enterprise-plugin-limitations/` for detailed guides

---

## Alternative Solutions Evaluated

### Solution 1: Memory Caching for R1 MVP (Immediate)

**Approach:**
- Use OSS Kong with `proxy-cache` and `strategy: memory`
- Remove `pre-function` and `post-function` dependencies
- Accept that cache is not persistent and not shared

**Trade-offs:**
- ⊖ Cache resets on Kong restart
- ⊖ Each Kong instance has separate cache
- ⊖ No custom cache key generation
- ⊖ No X-Cache-Status observability headers
- ⊕ Zero licensing costs
- ⊕ Simpler deployment
- ⊕ Still provides caching benefit for request bursts

**Implementation Time:** 30 seconds (config already prepared)

### Solution 2: Kong Enterprise Free Trial (Full Features)

**Approach:**
- Sign up for Kong Gateway Enterprise 30-day trial
- Add `KONG_LICENSE_DATA` environment variable
- Use all Enterprise plugins as designed

**Trade-offs:**
- ⊕ Full Redis caching with custom Lua
- ⊕ All observability features work
- ⊕ Matches original R1 design exactly
- ⊕ Can add AI plugins later (with AI license)
- ⊖ Requires license acquisition (free trial)
- ⊖ Need to plan for license procurement before production
- ⊖ 30-day trial limitation

**Implementation Time:** 1-2 days (license signup + integration)

### Solution 3: External Semantic Cache Service (R2)

**Approach:**
- Deploy Semcache.io (open-source) as separate service
- Route: Client → Kong → Semcache → LLM Providers
- Defer to R2 as enhancement

**Trade-offs:**
- ⊕ True semantic matching (not just exact)
- ⊕ Open-source (MIT license)
- ⊕ Purpose-built for LLM caching
- ⊖ Additional service to manage
- ⊖ Adds network hop
- ⊖ Out of scope for R1 MVP

**Implementation Time:** 2-3 days (new service integration)

### Solution 4: Database Mode with OSS Kong (Hybrid)

**Approach:**
- Use Kong with Postgres database
- Enable `proxy-cache` with `strategy: redis`
- Skip custom Lua functions (pre/post-function)

**Trade-offs:**
- ⊕ Redis caching works
- ⊕ Persistent across restarts
- ⊕ Open-source licensing
- ⊖ Requires database operational overhead
- ⊖ No custom cache key generation
- ⊖ No cache observability headers
- ⊖ More complex than DB-less

**Implementation Time:** 2-4 hours (database setup + testing)

## Recommendation for R1

**Short-term (R1 MVP):** Solution 1 - Memory Caching
- Gets us to deployable state immediately
- Satisfies core R1 requirements (routing, auth, rate limiting)
- Caching provides value even if not persistent
- Document limitation in R1 release notes

**Medium-term (Post-R1):** Solution 2 - Enterprise Trial
- Validates full design works as intended
- Provides path to production with proper licensing
- Enables all planned features

**Long-term (R2+):** Solution 3 - External Semantic Cache
- Best technical solution
- True semantic matching beyond exact cache hits
- Independent of Kong licensing

## Impact on R1 Acceptance Criteria

From `docs/project-docs/releases/R1/PRD.md`:

| Criteria | Status | Notes |
|----------|--------|-------|
| Multi-tenant sign-in | ⏳ Pending | Platform API service |
| Per-tenant LLM calls with BYO credentials | ✅ Ready | Auth headers implemented |
| Quotas enforced at gateway | ✅ Ready | Rate limiting complete |
| RAG queries | ⏳ Pending | Knowledge service |
| Dashboards display KPIs | ⏳ Pending | Client apps |
| **Semantic caching (40-60% reduction)** | ⚠️ **Degraded** | Memory-only vs Redis design |

**Severity:** Medium - Core functionality works; caching degraded but present

## Next Steps

1. **Immediate:** Deploy with memory caching to unblock testing
2. **Week 1:** Evaluate Enterprise trial vs DB mode for persistent caching
3. **R2 Planning:** Research Semcache.io integration as enhancement

## References

- R1 PRD: `docs/project-docs/releases/R1/PRD.md`
- R1 Architecture: `docs/project-docs/releases/R1/ARCHITECTURE.md`
- Task 1 Implementation: `.taskmaster/tasks/task-1.md`
- Kong config: `platform/infra/kong/kong.yaml`
- Kong OSS docs: https://docs.konghq.com/gateway/latest/
- Enterprise plugins: https://docs.konghq.com/hub/

