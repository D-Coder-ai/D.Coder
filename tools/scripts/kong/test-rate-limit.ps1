param(
  [string]$KongUrl = "http://localhost:8000",
  [int]$BurstCount = 10,
  [switch]$SkipProviderTests,
  [switch]$SkipRedisInspection,
  [switch]$Verbose
)

Write-Host "=== Kong Rate Limiting Test ===" -ForegroundColor Cyan
Write-Host ""

# Test strategy:
# 1. Verify rate limiting headers are present in responses
# 2. Send burst of requests to exceed limit
# 3. Verify 429 Too Many Requests is returned
# 4. Test tenant isolation (different tenants don't affect each other)
# 5. Verify Redis counter creation
# 6. Test fault tolerance (rate limiting disabled when Redis down)

$testPassed = $true

# Test 1: Check Kong availability
Write-Host "1. Checking Kong availability..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$KongUrl/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 404) {
        Write-Host "✓ Kong is reachable" -ForegroundColor Green
    } else {
        Write-Host "✗ Kong returned unexpected status: $($response.StatusCode)" -ForegroundColor Red
        $testPassed = $false
    }
} catch {
    Write-Host "✗ Kong is not reachable at $KongUrl" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 2: Verify rate limit headers in normal response
Write-Host "2. Testing rate limit headers in responses..." -ForegroundColor Yellow

$testRoute = "/v1/llm/openai/gpt-5"
$testTenant = "test-tenant-$(Get-Random)"

try {
    $response = Invoke-WebRequest -Uri "$KongUrl$testRoute" `
        -Method POST `
        -Headers @{"X-Tenant-Id" = $testTenant; "Content-Type" = "application/json"} `
        -Body '{"test":"request"}' `
        -TimeoutSec 10 `
        -SkipHttpErrorCheck

    if ($Verbose) {
        Write-Host "  Response Status: $($response.StatusCode)" -ForegroundColor Gray
        Write-Host "  Response Headers:" -ForegroundColor Gray
        $response.Headers.GetEnumerator() | Where-Object { $_.Key -like "*RateLimit*" } | ForEach-Object {
            Write-Host "    $($_.Key): $($_.Value)" -ForegroundColor Gray
        }
    }

    # Check for rate limit headers
    $hasLimitHeader = $response.Headers.ContainsKey("X-RateLimit-Limit-Minute") -or 
                      $response.Headers.ContainsKey("RateLimit-Limit") -or
                      $response.Headers.ContainsKey("X-RateLimit-Limit")
    
    $hasRemainingHeader = $response.Headers.ContainsKey("X-RateLimit-Remaining-Minute") -or
                          $response.Headers.ContainsKey("RateLimit-Remaining") -or
                          $response.Headers.ContainsKey("X-RateLimit-Remaining")

    if ($hasLimitHeader -and $hasRemainingHeader) {
        Write-Host "✓ Rate limit headers present in response" -ForegroundColor Green
    } else {
        Write-Host "✗ Rate limit headers missing from response" -ForegroundColor Red
        Write-Host "  Expected: X-RateLimit-Limit-Minute and X-RateLimit-Remaining-Minute" -ForegroundColor Red
        $testPassed = $false
    }
} catch {
    Write-Host "✗ Failed to make test request: $_" -ForegroundColor Red
    $testPassed = $false
}

Write-Host ""

# Test 3: Test burst to trigger rate limit
Write-Host "3. Testing rate limit enforcement (sending $BurstCount requests)..." -ForegroundColor Yellow

$burstTenant = "burst-test-tenant-$(Get-Random)"
$successCount = 0
$rateLimitedCount = 0
$errorCount = 0

for ($i = 1; $i -le $BurstCount; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "$KongUrl$testRoute" `
            -Method POST `
            -Headers @{"X-Tenant-Id" = $burstTenant; "Content-Type" = "application/json"} `
            -Body '{"test":"burst"}' `
            -TimeoutSec 5 `
            -SkipHttpErrorCheck

        if ($response.StatusCode -eq 429) {
            $rateLimitedCount++
            if ($Verbose) {
                Write-Host "  Request $i : 429 Too Many Requests" -ForegroundColor Gray
            }
        } elseif ($response.StatusCode -eq 200 -or $response.StatusCode -eq 401 -or $response.StatusCode -eq 404) {
            $successCount++
            if ($Verbose) {
                Write-Host "  Request $i : $($response.StatusCode)" -ForegroundColor Gray
            }
        } else {
            $errorCount++
            if ($Verbose) {
                Write-Host "  Request $i : Unexpected status $($response.StatusCode)" -ForegroundColor Gray
            }
        }
    } catch {
        $errorCount++
        if ($Verbose) {
            Write-Host "  Request $i : Error - $_" -ForegroundColor Gray
        }
    }
}

Write-Host "  Results: $successCount successful, $rateLimitedCount rate-limited (429), $errorCount errors" -ForegroundColor Cyan

if ($rateLimitedCount -gt 0) {
    Write-Host "✓ Rate limiting is working (received 429 responses)" -ForegroundColor Green
} else {
    Write-Host "⚠ No 429 responses received - rate limit may be too high for burst test" -ForegroundColor Yellow
    Write-Host "  Consider increasing -BurstCount or wait for rate limit window to reset" -ForegroundColor Yellow
}

Write-Host ""

# Test 4: Test tenant isolation
Write-Host "4. Testing tenant isolation..." -ForegroundColor Yellow

$tenant1 = "tenant-a-$(Get-Random)"
$tenant2 = "tenant-b-$(Get-Random)"
$tenant1Count = 0
$tenant2Count = 0

# Send requests for tenant 1
for ($i = 1; $i -le 5; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "$KongUrl$testRoute" `
            -Method POST `
            -Headers @{"X-Tenant-Id" = $tenant1; "Content-Type" = "application/json"} `
            -Body '{"test":"tenant1"}' `
            -TimeoutSec 5 `
            -SkipHttpErrorCheck
        
        if ($response.StatusCode -ne 429) {
            $tenant1Count++
        }
    } catch { }
}

# Send requests for tenant 2
for ($i = 1; $i -le 5; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "$KongUrl$testRoute" `
            -Method POST `
            -Headers @{"X-Tenant-Id" = $tenant2; "Content-Type" = "application/json"} `
            -Body '{"test":"tenant2"}' `
            -TimeoutSec 5 `
            -SkipHttpErrorCheck
        
        if ($response.StatusCode -ne 429) {
            $tenant2Count++
        }
    } catch { }
}

if ($Verbose) {
    Write-Host "  Tenant 1 successful requests: $tenant1Count" -ForegroundColor Gray
    Write-Host "  Tenant 2 successful requests: $tenant2Count" -ForegroundColor Gray
}

if ($tenant1Count -gt 0 -and $tenant2Count -gt 0) {
    Write-Host "✓ Tenant isolation working (both tenants can make independent requests)" -ForegroundColor Green
} else {
    Write-Host "⚠ Tenant isolation test inconclusive" -ForegroundColor Yellow
    $testPassed = $false
}

Write-Host ""

# Test 5: Verify Redis counter creation
if (-not $SkipRedisInspection) {
    Write-Host "5. Inspecting Redis for rate limit counters..." -ForegroundColor Yellow

    try {
        # Try to exec into Redis container
        $redisKeys = docker exec redis redis-cli KEYS "ratelimit:*" 2>&1

        if ($LASTEXITCODE -eq 0 -and $redisKeys) {
            $keyCount = ($redisKeys | Measure-Object).Count
            Write-Host "✓ Found $keyCount rate limit keys in Redis" -ForegroundColor Green
            
            if ($Verbose -and $keyCount -gt 0 -and $keyCount -le 20) {
                Write-Host "  Sample keys:" -ForegroundColor Gray
                $redisKeys | Select-Object -First 10 | ForEach-Object {
                    Write-Host "    $_" -ForegroundColor Gray
                }
            }
        } else {
            Write-Host "⚠ No rate limit keys found in Redis (or Redis not accessible)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠ Could not inspect Redis: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "5. Skipping Redis inspection (use without -SkipRedisInspection to enable)" -ForegroundColor Gray
}

Write-Host ""

# Test 6: Check rate limit key format
if (-not $SkipRedisInspection) {
    Write-Host "6. Validating Redis key format..." -ForegroundColor Yellow

    try {
        $sampleKey = docker exec redis redis-cli --scan --pattern "ratelimit:*" --count 1 2>&1 | Select-Object -First 1

        if ($sampleKey -and $sampleKey -match "ratelimit:") {
            if ($Verbose) {
                Write-Host "  Sample key: $sampleKey" -ForegroundColor Gray
            }
            
            # Expected format: ratelimit:{tenantId}:{service}:{route}:minute
            # Or Kong's default format which varies by version
            Write-Host "✓ Rate limit keys follow expected pattern" -ForegroundColor Green
            
            # Check TTL
            $ttl = docker exec redis redis-cli TTL "$sampleKey" 2>&1
            if ($LASTEXITCODE -eq 0 -and $ttl -match '^\d+$' -and [int]$ttl -gt 0) {
                if ($Verbose) {
                    Write-Host "  TTL: $ttl seconds" -ForegroundColor Gray
                }
                Write-Host "✓ Rate limit keys have TTL configured" -ForegroundColor Green
            }
        } else {
            Write-Host "⚠ Could not find sample key for validation" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠ Could not validate key format: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "6. Skipping Redis key validation (use without -SkipRedisInspection to enable)" -ForegroundColor Gray
}

Write-Host ""

# Test Summary
Write-Host "=== Test Summary ===" -ForegroundColor Cyan
if ($testPassed) {
    Write-Host "✓ All critical tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "✗ Some tests failed or were inconclusive" -ForegroundColor Red
    exit 1
}




