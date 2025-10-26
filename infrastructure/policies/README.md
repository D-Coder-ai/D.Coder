# Kong OPA Policies

This directory contains OPA/Rego policies for validating Kong declarative configurations.

## Policy: kong_services.rego

Enforces that all Kong service upstreams point only to allowlisted provider hosts.

### Allowed Hosts (R1)
- `api.openai.com`
- `api.anthropic.com`
- `generativelanguage.googleapis.com`
- `api.groq.com`

### Testing

**Validate current config:**
```powershell
conftest test infra/kong/kong-with-allowlist.yaml -p infra/policies --all-namespaces
```

Expected output: `1 test, 1 passed, 0 warnings, 0 failures, 0 exceptions`

**Test policy enforcement (should fail):**
```powershell
conftest test infra/kong/kong-invalid-test.yaml -p infra/policies --all-namespaces
```

Expected output: `1 test, 0 passed, 0 warnings, 1 failure` with message about disallowed host.

### CI Integration

Add to CI pipeline:
```yaml
- name: Validate Kong Config
  run: conftest test infra/kong/kong-with-allowlist.yaml -p infra/policies --all-namespaces
```

This ensures no unauthorized LLM provider endpoints can be deployed.

