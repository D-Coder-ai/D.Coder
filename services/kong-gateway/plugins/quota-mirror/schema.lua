-- Quota Mirror Plugin Schema
-- Defines configuration schema for the quota mirror plugin
-- This plugin mirrors quota usage from LiteLLM to Redis for alert monitoring

local typedefs = require "kong.db.schema.typedefs"

return {
  name = "quota-mirror",
  fields = {
    { consumer = typedefs.no_consumer },
    { protocols = typedefs.protocols_http },
    { config = {
        type = "record",
        fields = {
          { redis_host = { type = "string", required = true, default = "redis" } },
          { redis_port = { type = "integer", required = true, default = 6379 } },
          { redis_database = { type = "integer", required = true, default = 0 } },
          { redis_timeout = { type = "integer", required = true, default = 2000 } },
          { redis_password = { type = "string", required = false } },
          { redis_ssl = { type = "boolean", required = true, default = false } },
          { quota_key_prefix = { type = "string", required = true, default = "quota:tenant:" } },
          { alert_threshold_percentage = { type = "number", required = true, default = 80.0 } },
          { enable_alerts = { type = "boolean", required = true, default = true } },
          { block_on_quota_exceeded = { type = "boolean", required = true, default = false } }, -- R1: alert-only
          { log_quota_checks = { type = "boolean", required = true, default = true } },
        },
      },
    },
  },
}
