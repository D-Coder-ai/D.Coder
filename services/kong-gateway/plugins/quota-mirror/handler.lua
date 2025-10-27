-- Quota Mirror Plugin Handler
-- Mirrors quota usage from LiteLLM quota.updated events
-- R1: Alert-only mode (no request blocking)

local BasePlugin = require "kong.plugins.base_plugin"
local redis = require "resty.redis"

local QuotaMirrorHandler = BasePlugin:extend()

QuotaMirrorHandler.VERSION = "1.0.0"
QuotaMirrorHandler.PRIORITY = 900  -- Run before rate limiting (1000)

-- Initialize Redis connection
local function connect_redis(conf)
  local red = redis:new()
  red:set_timeout(conf.redis_timeout)

  local ok, err = red:connect(conf.redis_host, conf.redis_port)
  if not ok then
    kong.log.err("Failed to connect to Redis: ", err)
    return nil, err
  end

  -- Authenticate if password is provided
  if conf.redis_password then
    local res, err = red:auth(conf.redis_password)
    if not res then
      kong.log.err("Failed to authenticate with Redis: ", err)
      return nil, err
    end
  end

  -- Select database
  local ok, err = red:select(conf.redis_database)
  if not ok then
    kong.log.err("Failed to select Redis database: ", err)
    return nil, err
  end

  return red
end

-- Close Redis connection or return to pool
local function close_redis(red)
  if not red then
    return
  end

  -- Put connection back into pool
  local ok, err = red:set_keepalive(10000, 100)
  if not ok then
    kong.log.err("Failed to set keepalive: ", err)
  end
end

-- Get tenant quota from Redis
local function get_tenant_quota(red, tenant_id, conf)
  local quota_key = conf.quota_key_prefix .. tenant_id

  -- Get quota data from Redis hash
  local quota_data, err = red:hgetall(quota_key)
  if err then
    kong.log.err("Failed to get quota from Redis: ", err)
    return nil, err
  end

  -- Convert Redis array response to Lua table
  local quota = {}
  for i = 1, #quota_data, 2 do
    quota[quota_data[i]] = quota_data[i + 1]
  end

  return quota
end

-- Check if quota is exceeded or near threshold
local function check_quota_status(quota, conf)
  if not quota.limit or not quota.used then
    return false, 0
  end

  local limit = tonumber(quota.limit)
  local used = tonumber(quota.used)

  if limit <= 0 then
    return false, 0
  end

  local usage_percentage = (used / limit) * 100

  -- Check if exceeded
  if used >= limit then
    return true, usage_percentage
  end

  -- Check if near threshold
  if usage_percentage >= conf.alert_threshold_percentage then
    return true, usage_percentage
  end

  return false, usage_percentage
end

-- Plugin access phase - check quota before request
function QuotaMirrorHandler:access(conf)
  QuotaMirrorHandler.super.access(self)

  -- Get tenant ID from header
  local tenant_id = kong.request.get_header("X-Tenant-Id")
  if not tenant_id then
    kong.log.warn("No X-Tenant-Id header found, skipping quota check")
    return
  end

  -- Connect to Redis
  local red, err = connect_redis(conf)
  if not red then
    kong.log.err("Redis connection failed, allowing request (fail-open)")
    return  -- Fail open in R1
  end

  -- Get tenant quota
  local quota, err = get_tenant_quota(red, tenant_id, conf)
  if err then
    close_redis(red)
    kong.log.err("Failed to retrieve quota, allowing request")
    return
  end

  close_redis(red)

  -- Check quota status
  local quota_exceeded, usage_percentage = check_quota_status(quota, conf)

  -- Log quota check
  if conf.log_quota_checks then
    kong.log.info(string.format(
      "Quota check for tenant %s: used=%s, limit=%s, usage=%.2f%%",
      tenant_id,
      quota.used or "unknown",
      quota.limit or "unknown",
      usage_percentage
    ))
  end

  -- Add quota info to response headers
  kong.response.set_header("X-Quota-Limit", quota.limit or "unknown")
  kong.response.set_header("X-Quota-Used", quota.used or "unknown")
  kong.response.set_header("X-Quota-Remaining",
    tonumber(quota.limit or 0) - tonumber(quota.used or 0))
  kong.response.set_header("X-Quota-Usage-Percentage",
    string.format("%.2f", usage_percentage))

  -- R1: Alert only, don't block
  if quota_exceeded and conf.enable_alerts then
    kong.log.warn(string.format(
      "QUOTA ALERT: Tenant %s quota exceeded or near threshold (%.2f%%)",
      tenant_id,
      usage_percentage
    ))

    -- Add warning header (but don't block request)
    kong.response.set_header("X-Quota-Warning",
      string.format("Quota usage at %.2f%%", usage_percentage))
  end

  -- R1: Never block requests (alert-only mode)
  -- In R2+, if conf.block_on_quota_exceeded is true, return 429
  -- if quota_exceeded and conf.block_on_quota_exceeded then
  --   return kong.response.exit(429, {
  --     error = {
  --       code = "quota_exceeded",
  --       message = "Tenant quota exceeded",
  --       details = {
  --         usage_percentage = usage_percentage,
  --         limit = quota.limit,
  --         used = quota.used
  --       }
  --     }
  --   })
  -- end
end

return QuotaMirrorHandler
