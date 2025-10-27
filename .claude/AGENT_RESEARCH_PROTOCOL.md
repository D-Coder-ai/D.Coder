# Agent Research Protocol

**MANDATORY for all D.Coder agents when working with libraries, frameworks, or external dependencies.**

## Research-First Development Rule

**NEVER assume you know how a library works. ALWAYS research first.**

Before implementing any feature using an external library or service:
1. ✅ Research using Context7 MCP for official documentation
2. ✅ Use Exa MCP for best practices and recent discussions
3. ✅ Verify the feature is in the OSS/Free version (not Enterprise/Paywalled)
4. ✅ Document what you learned

## Step-by-Step Research Workflow

### Step 1: Use Context7 MCP for Official Documentation

**When to use Context7:**
- ANY time you're using a library, framework, or API
- Before implementing a feature
- When debugging or troubleshooting
- When unsure about configuration options

**How to use Context7:**
```typescript
// First, resolve the library ID
mcp__context7__resolve-library-id({
  libraryName: "langchain"
})

// Then get documentation with focused query
mcp__context7__get-library-docs({
  context7CompatibleLibraryID: "/langchain/langchainjs",
  topic: "document loaders configuration",
  tokens: 5000
})
```

**Examples:**
- FastAPI: `libraryName: "fastapi"` → topic: "dependency injection"
- LiteLLM: `libraryName: "litellm"` → topic: "semantic caching configuration"
- Temporal: `libraryName: "temporal"` → topic: "workflow durability"
- Kong: `libraryName: "kong gateway"` → topic: "declarative configuration"

### Step 2: Use Exa MCP for Best Practices

**When to use Exa:**
- Find recent discussions or blog posts about implementation patterns
- Discover common pitfalls or gotchas
- Find working examples or tutorials
- Check for recent updates or breaking changes

**How to use Exa:**
```typescript
mcp__plugin_exa-mcp-server_exa__get_code_context_exa({
  query: "LiteLLM semantic caching with Redis configuration best practices",
  tokensNum: 5000
})

mcp__plugin_exa-mcp-server_exa__web_search_exa({
  query: "Kong Gateway OSS rate limiting plugin configuration 2024",
  numResults: 5
})
```

**Examples:**
- "Temporal workflow error handling patterns Python"
- "FastAPI SQLAlchemy async session management best practices"
- "LangGraph agent state management examples"
- "pgvector performance tuning for semantic search"

### Step 3: Verify OSS/Free vs. Enterprise Features

**CRITICAL: R1 requires 100% open-source stack. NO enterprise/paywalled features.**

#### OSS Verification Checklist

For EVERY library feature you use, verify:
- [ ] Feature exists in OSS/Community/Free version
- [ ] Not marked as "Enterprise", "Cloud", "Premium", "Pro"
- [ ] License is permissive (MIT, Apache 2.0, BSD, not AGPL if used as service)
- [ ] No hidden costs or API keys required (beyond standard provider keys)

#### How to Verify

**Check official documentation:**
```typescript
// Use Context7 to check feature availability
mcp__context7__get-library-docs({
  context7CompatibleLibraryID: "/kong/kong",
  topic: "rate limiting plugin availability in OSS version",
  tokens: 3000
})
```

**Search for licensing information:**
```typescript
// Use Exa to find licensing info
mcp__plugin_exa-mcp-server_exa__web_search_exa({
  query: "Kong Gateway rate-limiting plugin OSS vs Enterprise 2024",
  numResults: 3
})
```

**Red flags indicating Enterprise/Paywalled:**
- Documentation says "Enterprise only"
- Feature listed in pricing comparison tables
- Requires license key or activation
- Only available in "Cloud" or "Hosted" versions
- Documentation URL contains "/enterprise/" or "/cloud/"

#### Known OSS vs. Enterprise Splits (R1 Stack)

**Kong Gateway:**
- ✅ OSS: Basic routing, rate limiting, JWT auth, request transformer, declarative config
- ❌ Enterprise: Advanced rate limiting, RBAC, Dev Portal, Vitals, OpenID Connect, SAML

**LiteLLM (MIT License):**
- ✅ OSS: All routing, caching, callbacks, streaming, virtual keys
- ⚠️  Paid: LiteLLM Proxy UI (optional, not required for R1)

**Temporal:**
- ✅ OSS: Workflows, activities, workers, retries, signals, queries
- ❌ Cloud: Multi-region, dedicated clusters, priority support (use OSS self-hosted in R1)

**Agenta:**
- ✅ OSS: Prompt playground, evaluations, A/B testing
- ❌ Cloud: Hosted version (use self-hosted in R1)

**PostgreSQL:**
- ✅ OSS: Everything including pgvector extension
- No enterprise split

**Logto:**
- ✅ OSS: OIDC, social logins, MFA, user management
- ❌ Cloud: Managed hosting, SLA (use self-hosted in R1)

**Flagsmith:**
- ✅ OSS: All feature flags, segments, A/B tests
- ❌ Cloud: Managed hosting (use self-hosted in R1)

### Step 4: Document Your Research

**In Linear story comments or commit messages:**
```markdown
## Research Done
- Context7: Verified LiteLLM semantic caching is in OSS version (MIT license)
- Exa: Found best practices for Redis configuration with TTL settings
- OSS Verification: ✅ All features used are in open-source version
- Source: https://docs.litellm.ai/docs/caching
```

## Examples of Proper Research

### Example 1: Implementing LiteLLM Caching

❌ **Wrong approach:**
```
# Agent immediately implements caching config without research
# Assumes semantic caching is available
# Doesn't verify OSS vs. paid
```

✅ **Correct approach:**
```typescript
// 1. Research with Context7
mcp__context7__resolve-library-id({ libraryName: "litellm" })
mcp__context7__get-library-docs({
  context7CompatibleLibraryID: "/litellm/litellm",
  topic: "semantic caching redis configuration",
  tokens: 5000
})

// 2. Find examples with Exa
mcp__plugin_exa-mcp-server_exa__get_code_context_exa({
  query: "LiteLLM Redis semantic caching configuration python example",
  tokensNum: 5000
})

// 3. Verify OSS
mcp__plugin_exa-mcp-server_exa__web_search_exa({
  query: "LiteLLM semantic caching MIT license open source",
  numResults: 3
})

// 4. Document findings
// "Verified: Semantic caching is in OSS LiteLLM (MIT license).
// Redis backend supported. TTL configurable. No enterprise features required."

// 5. NOW implement with confidence
```

### Example 2: Configuring Kong Gateway Plugin

✅ **Correct approach:**
```typescript
// 1. Check if rate-limiting plugin is in Kong OSS
mcp__context7__resolve-library-id({ libraryName: "kong gateway" })
mcp__context7__get-library-docs({
  context7CompatibleLibraryID: "/kong/kong",
  topic: "rate limiting plugin OSS availability",
  tokens: 3000
})

// 2. Find configuration examples
mcp__plugin_exa-mcp-server_exa__get_code_context_exa({
  query: "Kong Gateway OSS rate limiting plugin declarative configuration yaml",
  tokensNum: 5000
})

// 3. Verify not enterprise-only
mcp__plugin_exa-mcp-server_exa__web_search_exa({
  query: "Kong Gateway rate-limiting plugin OSS vs Enterprise comparison",
  numResults: 3
})

// 4. Document: "Rate limiting plugin confirmed in Kong OSS.
// Redis policy supported. No enterprise license required."
```

### Example 3: Using Temporal Workflows

✅ **Correct approach:**
```typescript
// 1. Research Temporal Python SDK
mcp__context7__resolve-library-id({ libraryName: "temporal" })
mcp__context7__get-library-docs({
  context7CompatibleLibraryID: "/temporalio/sdk-python",
  topic: "durable workflow execution and error handling",
  tokens: 6000
})

// 2. Find patterns
mcp__plugin_exa-mcp-server_exa__get_code_context_exa({
  query: "Temporal Python workflow retry policy error handling examples",
  tokensNum: 5000
})

// 3. Verify self-hosted works (no cloud required)
// "Temporal OSS server provides all workflow features.
// No Temporal Cloud subscription needed for R1."
```

## Failure Modes to Avoid

❌ **Don't do this:**
1. "I remember how FastAPI works" → Research anyway, versions change
2. "I'll just try this config" → Research first, verify it exists in OSS
3. "This should work" → Verify with docs and examples
4. "I saw this in another project" → Verify it applies to your version
5. "The error message says..." → Research the proper solution

✅ **Do this:**
1. Always use Context7 for official docs
2. Always use Exa for real-world examples
3. Always verify OSS vs. Enterprise
4. Always document your research
5. Ask r1-technical-architect if uncertain about license compliance

## When to Ask r1-technical-architect

If after research you're uncertain:
- "Is this feature acceptable for R1 OSS requirements?"
- "This feature seems like it might be enterprise, can you verify?"
- "I found conflicting information about licensing"
- "Should we use this library or find an alternative?"

## Research Time Budget

**Expect to spend:**
- 5-10 minutes: Simple feature in familiar library
- 15-30 minutes: Complex feature or new library
- 30-60 minutes: Major architectural decision

**This is time well spent.** Research prevents:
- Implementing enterprise features that break R1 requirements
- Using wrong APIs or deprecated patterns
- Rework and debugging
- License compliance issues

## Summary Checklist

Before implementing ANY feature with external dependency:

- [ ] Used Context7 MCP to get official documentation
- [ ] Used Exa MCP to find best practices and examples
- [ ] Verified feature is in OSS/Free version (not Enterprise/Paywalled)
- [ ] Documented research findings
- [ ] Confident the implementation will work and is compliant with R1

**Only proceed with implementation after completing ALL checklist items.**
