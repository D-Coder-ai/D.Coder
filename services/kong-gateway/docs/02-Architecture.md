 # Architecture
 
 - Declarative Kong config rendered to `config/kong.yml`
 - Upstreams: platform services; Routes: `/v1/*`, health, metrics
 - Plugins: rate-limiting (Redis), prometheus, correlation-id, http-log
 - Admin API at 8001 for status and debugging
 
 References: [Kong Docs](https://docs.konghq.com/) • [Service README](../README.md)
