# Kong AI Gateway — R1 Allowlisted Provider Services

This folder contains the declarative `kong.yaml` for R1 with only the approved upstream provider services.

Admin API hardening (for Docker Compose):

```yaml
environment:
  KONG_ENFORCE_RBAC: "on"
  KONG_ADMIN_LISTEN: "127.0.0.1:8001"
  KONG_STATUS_LISTEN: "0.0.0.0:8100"
  # KONG_RBAC_ADMIN_TOKEN: ${KONG_ADMIN_TOKEN}
```

Notes:
- Do not expose the Admin API publicly.
- No routes/plugins are defined here (added in the next subtask).
- Upstream provider hostnames are enforced via OPA/Conftest policy under `../policies`.


