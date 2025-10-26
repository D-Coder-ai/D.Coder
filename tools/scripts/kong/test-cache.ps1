# Kong LLM Semantic Cache Testing Script
# Tests cache MISS/HIT behavior, tenant isolation, provider isolation, and parameter sensitivity

param(
    [string]$KongUrl = "http://localhost:8000",
    [switch]$SkipRedisInspection,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

# ANSI color codes
$Green = "`e[32m"
$Red = "`e[31m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-TestHeader {
    param([string]$Message)
    Write-Host "`n$Blue==================== $Message ====================$Reset"
}

function Write-Success {
    param([string]$Message)
    Write-Host "$Green✓ $Message$Reset"
}

function Write-Failure {
    param([string]$Message)
    Write-Host "$Red✗ $Message$Reset"
}

function Write-Info {
    param([string]$Message)
    Write-Host "$Yellow→ $Message$Reset"
}

# Test counter
$script:TestsPassed = 0
$script:TestsFailed = 0

function Assert-Equal {
    param(
        [string]$Actual,
        [string]$Expected,
        [string]$TestName
    )
    
    if ($Actual -eq $Expected) {
        Write-Success "$TestName"
        $script:TestsPassed++
    } else {
        Write-Failure "$TestName - Expected: $Expected, Got: $Actual"
        $script:TestsFailed++
    }
}

# Check Kong availability
Write-TestHeader "Checking Kong Availability"
try {
    $response = Invoke-WebRequest -Uri "$KongUrl/" -Method GET -TimeoutSec 5
    Write-Success "Kong is reachable at $KongUrl"
} catch {
    Write-Failure "Kong is not reachable at $KongUrl"
    exit 1
}

# Test 1: Cache MISS → HIT for identical requests
Write-TestHeader "Test 1: Cache MISS → HIT Behavior"

$testBody = @{
    messages = @(
        @{
            role = "user"
            content = "What is 2+2? Answer in one word."
        }
    )
    model = "gpt-5"
    temperature = 0.7
} | ConvertTo-Json -Compress

$headers = @{
    "Content-Type" = "application/json"
    "X-Tenant-Id" = "test-tenant-cache"
}

Write-Info "Sending first request (should be MISS)..."
try {
    $response1 = Invoke-WebRequest -Uri "$KongUrl/v1/llm/openai/gpt-5" `
        -Method POST `
        -Body $testBody `
        -Headers $headers `
        -SkipHttpErrorCheck
    
    $cacheStatus1 = $response1.Headers['X-Cache-Status']
    if ($Verbose) {
        Write-Host "First request - Status: $($response1.StatusCode), X-Cache-Status: $cacheStatus1"
    }
    Assert-Equal -Actual $cacheStatus1 -Expected "MISS" -TestName "First request returns cache MISS"
    
    # Wait a moment for cache to be written
    Start-Sleep -Seconds 1
    
    Write-Info "Sending identical second request (should be HIT)..."
    $response2 = Invoke-WebRequest -Uri "$KongUrl/v1/llm/openai/gpt-5" `
        -Method POST `
        -Body $testBody `
        -Headers $headers `
        -SkipHttpErrorCheck
    
    $cacheStatus2 = $response2.Headers['X-Cache-Status']
    if ($Verbose) {
        Write-Host "Second request - Status: $($response2.StatusCode), X-Cache-Status: $cacheStatus2"
    }
    Assert-Equal -Actual $cacheStatus2 -Expected "HIT" -TestName "Second identical request returns cache HIT"
    
} catch {
    Write-Failure "Test 1 failed with error: $($_.Exception.Message)"
    $script:TestsFailed++
}

# Test 2: Tenant Isolation
Write-TestHeader "Test 2: Tenant Isolation"

$headersTenant2 = @{
    "Content-Type" = "application/json"
    "X-Tenant-Id" = "different-tenant"
}

Write-Info "Sending same request with different tenant ID (should be MISS)..."
try {
    $response3 = Invoke-WebRequest -Uri "$KongUrl/v1/llm/openai/gpt-5" `
        -Method POST `
        -Body $testBody `
        -Headers $headersTenant2 `
        -SkipHttpErrorCheck
    
    $cacheStatus3 = $response3.Headers['X-Cache-Status']
    if ($Verbose) {
        Write-Host "Different tenant request - Status: $($response3.StatusCode), X-Cache-Status: $cacheStatus3"
    }
    Assert-Equal -Actual $cacheStatus3 -Expected "MISS" -TestName "Different tenant ID returns cache MISS"
    
} catch {
    Write-Failure "Test 2 failed with error: $($_.Exception.Message)"
    $script:TestsFailed++
}

# Test 3: Provider Isolation
Write-TestHeader "Test 3: Provider Isolation"

Write-Info "Sending same prompt to different provider (should be MISS)..."
try {
    # Same prompt structure but to Groq provider
    $response4 = Invoke-WebRequest -Uri "$KongUrl/v1/llm/groq/gpt-oss-120b" `
        -Method POST `
        -Body $testBody `
        -Headers $headers `
        -SkipHttpErrorCheck
    
    $cacheStatus4 = $response4.Headers['X-Cache-Status']
    if ($Verbose) {
        Write-Host "Different provider request - Status: $($response4.StatusCode), X-Cache-Status: $cacheStatus4"
    }
    Assert-Equal -Actual $cacheStatus4 -Expected "MISS" -TestName "Different provider returns cache MISS"
    
} catch {
    Write-Failure "Test 3 failed with error: $($_.Exception.Message)"
    $script:TestsFailed++
}

# Test 4: Parameter Sensitivity
Write-TestHeader "Test 4: Parameter Sensitivity"

$differentTempBody = @{
    messages = @(
        @{
            role = "user"
            content = "What is 2+2? Answer in one word."
        }
    )
    model = "gpt-5"
    temperature = 0.9  # Different temperature
} | ConvertTo-Json -Compress

Write-Info "Sending same prompt with different temperature (should be MISS)..."
try {
    $response5 = Invoke-WebRequest -Uri "$KongUrl/v1/llm/openai/gpt-5" `
        -Method POST `
        -Body $differentTempBody `
        -Headers $headers `
        -SkipHttpErrorCheck
    
    $cacheStatus5 = $response5.Headers['X-Cache-Status']
    if ($Verbose) {
        Write-Host "Different temperature request - Status: $($response5.StatusCode), X-Cache-Status: $cacheStatus5"
    }
    Assert-Equal -Actual $cacheStatus5 -Expected "MISS" -TestName "Different temperature returns cache MISS"
    
} catch {
    Write-Failure "Test 4 failed with error: $($_.Exception.Message)"
    $script:TestsFailed++
}

# Test 5: Cache Key Format Inspection (if Redis inspection is enabled)
if (-not $SkipRedisInspection) {
    Write-TestHeader "Test 5: Redis Cache Key Inspection"
    
    Write-Info "Inspecting Redis for cache keys..."
    try {
        # Try to connect to Redis and inspect keys
        $redisKeys = docker exec redis redis-cli KEYS "llm:*" 2>$null
        
        if ($redisKeys) {
            Write-Success "Found $(($redisKeys -split "`n").Count) cache keys in Redis"
            if ($Verbose) {
                Write-Host "Sample keys:"
                ($redisKeys -split "`n") | Select-Object -First 5 | ForEach-Object {
                    Write-Host "  $_"
                }
            }
            
            # Check key format: llm:{tenantId}:{provider}:{model}:{hash}
            $keyPattern = "llm:test-tenant-cache:openai:gpt-5:"
            $matchingKeys = $redisKeys -split "`n" | Where-Object { $_ -like "$keyPattern*" }
            
            if ($matchingKeys) {
                Write-Success "Cache keys follow expected format: llm:{tenantId}:{provider}:{model}:{hash}"
            } else {
                Write-Failure "No keys found matching expected format"
                $script:TestsFailed++
            }
            
            # Check TTL of a key
            if ($matchingKeys) {
                $sampleKey = $matchingKeys[0]
                $ttl = docker exec redis redis-cli TTL $sampleKey 2>$null
                if ($ttl -and $ttl -gt 0) {
                    Write-Success "Cache key has TTL: $ttl seconds (target: ~86400)"
                } else {
                    Write-Failure "Cache key TTL check failed"
                    $script:TestsFailed++
                }
            }
        } else {
            Write-Info "No cache keys found in Redis (tests may have failed earlier)"
        }
        
    } catch {
        Write-Info "Redis inspection skipped: $($_.Exception.Message)"
    }
}

# Test Summary
Write-TestHeader "Test Summary"
$totalTests = $script:TestsPassed + $script:TestsFailed

Write-Host ""
Write-Host "Total Tests: $totalTests"
Write-Host "$Green Passed: $script:TestsPassed$Reset"
Write-Host "$Red Failed: $script:TestsFailed$Reset"

if ($script:TestsFailed -eq 0) {
    Write-Host "`n$Green✓ All tests passed!$Reset"
    exit 0
} else {
    Write-Host "`n$Red✗ Some tests failed.$Reset"
    exit 1
}




