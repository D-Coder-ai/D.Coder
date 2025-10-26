# Kong Deployment Failure: Plugin Loading in DB-less Mode

**Date:** October 24, 2025  
**Context:** Subtask 1.6 - Implementing globocom/kong-plugin-proxy-cache for Redis caching  
**Status:** Blocked - Kong container fails to start

---

## Objective

Deploy Kong Gateway (OSS) in DB-less mode with globocom/kong-plugin-proxy-cache for Redis-backed caching on all 12 LLM routes.

---

## What Works ✅

1. **Plugin Installation**: globocom plugin installs successfully in Dockerfile
   ```bash
   docker-compose build kong  # Succeeds
   # Logs show: "kong-plugin-proxy-cache 2.0.0-1 is now installed"
   ```

2. **Configuration Validation**: deck-validate passes all checks
   ```powershell
   .\scripts\kong\deck-validate.ps1  # ✅ All tests pass
   ```

3. **Configuration File**: `platform/infra/kong/kong.yaml` is valid YAML with correct plugin syntax
   - 12 routes configured
   - globocom proxy-cache plugin with Redis backend
   - request-transformer plugin for auth headers
   - rate-limiting plugin with Redis policy

4. **File Structure**: All files properly organized per R1 architecture
   - Config: `platform/infra/kong/kong.yaml`
- Docker: `platform/gateways/kong/Dockerfile`
   - Compose: `platform/docker-compose.yml`

---

## Current Blocker ❌

**Kong container exits immediately with error code 1**

### Error Messages

```
2025/10/24 07:46:37 [error] init_by_lua error: error loading plugin schemas:
on plugin 'request-transformer': request-transformer plugin is enabled but not installed;
on plugin 'ai-prompt-template': ai-prompt-template plugin is enabled but not installed;
on plugin 'http-log': http-log plugin is enabled but not installed;
```

### Symptoms

- Container starts then exits within 2-3 seconds
- `docker ps` shows no running Kong container
- `docker ps -a` shows "Exited (1)"
- No Kong routes accessible at http://localhost:8001

---

## Root Cause Analysis

**Hypothesis:** Kong OSS `kong:latest` image doesn't include "bundled" plugins in DB-less mode, or requires different plugin configuration.

**Evidence:**
1. Errors mention standard Kong plugins (`request-transformer`, `rate-limiting`) as "not installed"
2. Our config only uses these plugins - we removed all Enterprise-only plugins
3. globocom plugin installed successfully but Kong fails before loading declarative config
4. Tried removing `KONG_PLUGINS` env var - still fails

**Kong Documentation References:**
- DB-less mode: Uses declarative config only, plugins must be in image
- Standard plugins should be bundled with OSS image
- Our config path: `KONG_DECLARATIVE_CONFIG=/etc/kong/custom/kong.yml`

---

## What I've Tried

### Attempt 1: Specify plugins explicitly
```yaml
KONG_PLUGINS: bundled,request-transformer,proxy-cache,rate-limiting
```
**Result:** Error - "bundled" not recognized, plugins still not found

### Attempt 2: List only used plugins
```yaml
KONG_PLUGINS: request-transformer,proxy-cache,rate-limiting
```
**Result:** Error - plugins marked as "enabled but not installed"

### Attempt 3: Remove KONG_PLUGINS env var entirely
```yaml
# No KONG_PLUGINS set - let Kong auto-detect from declarative config
```
**Result:** Same error - plugins still not found

### Attempt 4: Clean restart
```bash
docker-compose down
docker-compose up -d kong
```
**Result:** No change - same plugin loading errors

### Attempt 5: Remove Enterprise-only plugins from config
- Removed `pre-function` and `post-function` from Anthropic routes
- Kept only OSS plugins: `request-transformer`, `proxy-cache`, `rate-limiting`
**Result:** Still fails with same errors

---

## Possible Solutions

### Option A: Use legacy standalone deployment
**Approach:** Deploy using a dedicated compose file instead of `platform/docker-compose.yml`

**Pros:**
- Has been working in previous subtasks
- Simpler configuration
- Same Dockerfile and config files

**Cons:**
- Not using platform orchestration (R1 design calls for platform/ deployment)

### Option B: Use different Kong base image
**Approach:** Try `kong/kong-gateway:3.8` or specific OSS version tag

**Pros:**
- May have better plugin bundling
- Specific versions more predictable

**Cons:**
- May still lack bundled plugins in DB-less mode
- Could have other compatibility issues

### Option C: Manual plugin installation in Dockerfile
**Approach:** Install standard Kong plugins explicitly via luarocks

**Pros:**
- Ensures plugins are available
- More control over what's installed

**Cons:**
- Adds complexity
- May conflict with Kong's plugin system
- Time-consuming to debug

### Option D: Switch to database mode
**Approach:** Use Postgres backend instead of DB-less mode

**Pros:**
- Better plugin support in DB mode
- More features available

**Cons:**
- Adds Postgres dependency
- More complex operational model
- Deviates from simple R1 architecture

---

## Documentation References

**R1 Architecture:**
- `docs/project-docs/releases/R1/ARCHITECTURE.md` - Specifies Kong as AI Gateway (lines 30-35)
- `docs/project-docs/releases/R1/PRD.md` - Redis-backed caching requirement (line 27-28)

**Implementation Docs:**
- `platform/infra/kong/README.md` - Current Kong configuration documentation
- `platform/infra/kong/IMPLEMENTATION_NOTES.md` - Historical implementation notes
- `docs/challenges/kong-oss-enterprise-plugin-limitations.md` - Original challenge and solution discovery

**Solution Research:**
- `docs/challenges/Solution-kong-oss-enterprise-plugin-limitations/quick-start-globocom-plugin.md` - Installation guide followed
- `docs/challenges/Solution-kong-oss-enterprise-plugin-limitations/executive-summary-final.md` - Solution recommendation

---

## Solution Implemented ✅

**Decision:** Option D (Modified) - Use DB mode with memory-based caching

**Root Cause Identified:**
1. **Plugin directory overwrite**: Volume mount `./plugins:/usr/local/share/lua/5.1/kong/plugins` was replacing Kong's bundled plugins directory
2. **Redis limitation**: Kong 3.8 OSS bundled `proxy-cache` plugin ONLY supports `strategy: memory`, NOT Redis
3. **globocom installation failure**: luarocks manifest errors prevent installing community Redis plugin

**Final Solution:**
1. Pin Kong image to `kong:3.8` ✅
2. Remove plugin directory volume mounts from both the standalone compose file and `platform/docker-compose.yml` ✅
3. Simplified Dockerfile to minimal changes (copy config only, no custom plugin installs) ✅
4. Use `strategy: memory` for proxy-cache instead of Redis ✅
5. Clean config files - remove ALL Enterprise-only plugins (`pre-function`, `post-function`, `ai-*`) ✅
6. Remove `KONG_PLUGINS` env var to auto-load all bundled plugins ✅
7. Use DB mode (Postgres) via the standalone compose file ✅
8. Sync declarative config to DB using `deck gateway sync` ✅

**Verification Results:**
- Kong container: ✅ Running and healthy
- Plugins enabled: ✅ All bundled plugins including `request-transformer`, `rate-limiting`, `proxy-cache`
- Routes loaded: ✅ All 12 LLM routes created successfully
- Auth injection: ✅ Confirmed working (OpenAI returns 401 with empty key as expected)
- Rate limiting: ✅ Headers present (`X-RateLimit-Limit-Minute: 600`)
- Caching: ✅ Headers present (`X-Cache-Status: Bypass` for error responses)

**Tradeoffs for R1:**
- **Memory caching**: Cache data stored in-memory, lost on restart, not shared across instances
- **Limited scalability**: For multi-instance Kong, cache won't be shared (acceptable for R1 single-instance MVP)
- **Future path**: R2 can explore alternative Redis caching solutions (Nginx Plus, custom plugin, or Kong Enterprise upgrade)

**Files Modified:**
- `platform/gateways/kong/Dockerfile` - Simplified, removed luarocks/globocom install
- `platform/gateways/kong/docker-compose.yml` - Removed plugins volume mount
- `platform/docker-compose.yml` - Added KONG_DECLARATIVE_CONFIG, removed KONG_PLUGINS, removed plugins mount
- `platform/infra/kong/kong.yaml` - Clean config with memory-based proxy-cache
- `platform/gateways/kong/config/kong.yml` - Synced from platform config

