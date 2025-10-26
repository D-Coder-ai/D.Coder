# Platform and Tenant Configuration (R2)

## Additions in R2
- `providers.*.secretRef`: reference to Vault/KMS secret
- Archival: `archival.retentionDays`, `archival.exportEnabled`

## Layers
- Platform-level: defaults, plugin catalog
- Tenant-level: providers, quotas, flags, archival, UI branding

## Storage
- Platform config in config DB/store; tenant config in tenant DB

## Validation
- JSON Schema; read-only snapshots for services
