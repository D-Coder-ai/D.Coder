# Platform and Tenant Configuration (R3)

## New fields
- `residency.region`: region code for data placement
- `egress.allowlist`: array of allowed domains/endpoints
- `semanticCache`: { ttl, namespacePolicy: "tenant+provider+model" }

## Notes
- Applied at tenant creation; changing residency may require data migration plan
