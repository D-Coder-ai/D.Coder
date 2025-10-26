param(
  [string]$KongUrl = "http://localhost:8000",
  [switch]$SkipProviderTests = $false
)

Write-Host "=== Kong Authentication Testing ===" -ForegroundColor Cyan
Write-Host ""

# Check if Kong is reachable
Write-Host "1. Checking Kong availability..." -ForegroundColor Yellow
try {
    $statusResponse = Invoke-WebRequest -Uri "$KongUrl/health" -Method Get -ErrorAction Stop -TimeoutSec 5
    if ($statusResponse.StatusCode -eq 404) {
        Write-Host "✓ Kong is running" -ForegroundColor Green
    }
} catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 404) {
        Write-Host "✓ Kong is running" -ForegroundColor Green
    } else {
        Write-Error "Kong is not reachable at $KongUrl"
        Write-Host "Start Kong with: cd platform && docker-compose up -d kong" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""

# Check environment variables
Write-Host "2. Checking environment variables..." -ForegroundColor Yellow

$envVars = @{
    "OPENAI_API_KEY" = $env:OPENAI_API_KEY
    "ANTHROPIC_API_KEY" = $env:ANTHROPIC_API_KEY
    "GOOGLE_API_KEY" = $env:GOOGLE_API_KEY
    "GROQ_API_KEY" = $env:GROQ_API_KEY
}

$missingKeys = @()
foreach ($key in $envVars.Keys) {
    if ([string]::IsNullOrWhiteSpace($envVars[$key])) {
        Write-Host "⚠ $key not set (routes will fail with 401)" -ForegroundColor Yellow
        $missingKeys += $key
    } else {
        $maskedValue = $envVars[$key].Substring(0, [Math]::Min(10, $envVars[$key].Length)) + "..."
        Write-Host "✓ $key set ($maskedValue)" -ForegroundColor Green
    }
}

if ($missingKeys.Count -eq 4) {
    Write-Host ""
    Write-Host "⚠ No API keys configured!" -ForegroundColor Yellow
    Write-Host "See platform/gateways/kong/API_KEYS.md for setup instructions" -ForegroundColor Yellow
    if (-not $SkipProviderTests) {
        Write-Host "Use -SkipProviderTests to skip live provider testing" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""

# Test route configuration (auth headers presence)
Write-Host "3. Validating auth headers in Kong config..." -ForegroundColor Yellow

$routes = @(
    @{Provider="openai"; Model="gpt-5"; Path="/v1/llm/openai/gpt-5"},
    @{Provider="anthropic"; Model="claude-sonnet-4-5"; Path="/v1/llm/anthropic/claude-sonnet-4-5"},
    @{Provider="google"; Model="gemini-2-5-pro"; Path="/v1/llm/google/gemini-2-5-pro"},
    @{Provider="groq"; Model="gpt-oss-120b"; Path="/v1/llm/groq/gpt-oss-120b"}
)

$routeErrors = 0
foreach ($route in $routes) {
    try {
        # Send a test request (we expect it to reach the provider and potentially fail with auth/validation errors)
        $testBody = @{
            messages = @(
                @{role = "user"; content = "test"}
            )
        } | ConvertTo-Json
        
        $null = Invoke-WebRequest `
            -Uri "$KongUrl$($route.Path)" `
            -Method Post `
            -Body $testBody `
            -ContentType "application/json" `
            -Headers @{"X-Tenant-Id" = "test-tenant"} `
            -ErrorAction SilentlyContinue `
            -TimeoutSec 10
        
        # If we get here, the request was proxied (even if provider rejects it)
        Write-Host "✓ Route $($route.Path) is configured" -ForegroundColor Green
        
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        
        # 401/403 from provider means auth headers were sent (good)
        # 400/422 means validation errors (also acceptable - route works)
        # 404/502/503 means Kong routing issue (bad)
        
        if ($statusCode -in @(400, 401, 403, 422)) {
            Write-Host "✓ Route $($route.Path) is configured (provider responded with $statusCode)" -ForegroundColor Green
        } elseif ($statusCode -eq 404) {
            Write-Host "✗ Route $($route.Path) not found (404)" -ForegroundColor Red
            $routeErrors++
        } elseif ($statusCode -in @(502, 503, 504)) {
            Write-Host "⚠ Route $($route.Path) has upstream issues ($statusCode)" -ForegroundColor Yellow
        } else {
            Write-Host "⚠ Route $($route.Path) returned unexpected status: $statusCode" -ForegroundColor Yellow
        }
    }
}

if ($routeErrors -gt 0) {
    Write-Error "Some routes are not configured correctly"
    exit 1
}

Write-Host ""

# Test with live providers (if keys are set and not skipped)
if (-not $SkipProviderTests -and $missingKeys.Count -lt 4) {
    Write-Host "4. Testing live provider authentication..." -ForegroundColor Yellow
    Write-Host "   (This sends real API requests to verify auth headers work)" -ForegroundColor Gray
    Write-Host ""
    
    # OpenAI test
    if ($envVars["OPENAI_API_KEY"]) {
        Write-Host "  Testing OpenAI..." -NoNewline
        try {
            $openaiBody = @{
                input = @(
                    @{
                        role = "user"
                        content = @(@{type = "input_text"; text = "Say 'auth test passed' in 3 words"})
                    }
                )
                max_output_tokens = 10
            } | ConvertTo-Json -Depth 10
            
            $null = Invoke-WebRequest `
                -Uri "$KongUrl/v1/llm/openai/gpt-5" `
                -Method Post `
                -Body $openaiBody `
                -ContentType "application/json" `
                -Headers @{"X-Tenant-Id" = "test-tenant"} `
                -ErrorAction Stop `
                -TimeoutSec 30
            
            Write-Host " ✓ Authenticated successfully" -ForegroundColor Green
        } catch {
            $statusCode = $_.Exception.Response.StatusCode.value__
            if ($statusCode -eq 401) {
                Write-Host " ✗ Authentication failed (401 - check API key)" -ForegroundColor Red
            } else {
                Write-Host " ⚠ Request failed with status $statusCode" -ForegroundColor Yellow
            }
        }
    }
    
    # Anthropic test
    if ($envVars["ANTHROPIC_API_KEY"]) {
        Write-Host "  Testing Anthropic..." -NoNewline
        try {
            $anthropicBody = @{
                model = "claude-sonnet-4-5-20250929"
                max_tokens = 10
                messages = @(
                    @{role = "user"; content = "Say 'auth test passed' in 3 words"}
                )
            } | ConvertTo-Json -Depth 10
            
            $null = Invoke-WebRequest `
                -Uri "$KongUrl/v1/llm/anthropic/claude-sonnet-4-5" `
                -Method Post `
                -Body $anthropicBody `
                -ContentType "application/json" `
                -Headers @{"X-Tenant-Id" = "test-tenant"} `
                -ErrorAction Stop `
                -TimeoutSec 30
            
            Write-Host " ✓ Authenticated successfully" -ForegroundColor Green
        } catch {
            $statusCode = $_.Exception.Response.StatusCode.value__
            if ($statusCode -eq 401) {
                Write-Host " ✗ Authentication failed (401 - check API key)" -ForegroundColor Red
            } else {
                Write-Host " ⚠ Request failed with status $statusCode" -ForegroundColor Yellow
            }
        }
    }
    
    # Google test
    if ($envVars["GOOGLE_API_KEY"]) {
        Write-Host "  Testing Google..." -NoNewline
        try {
            $googleBody = @{
                contents = @(
                    @{
                        role = "user"
                        parts = @(@{text = "Say 'auth test passed' in 3 words"})
                    }
                )
            } | ConvertTo-Json -Depth 10
            
            $null = Invoke-WebRequest `
                -Uri "$KongUrl/v1/llm/google/gemini-2-5-pro" `
                -Method Post `
                -Body $googleBody `
                -ContentType "application/json" `
                -Headers @{"X-Tenant-Id" = "test-tenant"} `
                -ErrorAction Stop `
                -TimeoutSec 30
            
            Write-Host " ✓ Authenticated successfully" -ForegroundColor Green
        } catch {
            $statusCode = $_.Exception.Response.StatusCode.value__
            if ($statusCode -eq 401 -or $statusCode -eq 403) {
                Write-Host " ✗ Authentication failed ($statusCode - check API key)" -ForegroundColor Red
            } else {
                Write-Host " ⚠ Request failed with status $statusCode" -ForegroundColor Yellow
            }
        }
    }
    
    # Groq test
    if ($envVars["GROQ_API_KEY"]) {
        Write-Host "  Testing Groq..." -NoNewline
        try {
            $groqBody = @{
                model = "openai/gpt-oss-120b"
                messages = @(
                    @{role = "user"; content = "Say 'auth test passed' in 3 words"}
                )
                max_tokens = 10
            } | ConvertTo-Json -Depth 10
            
            $null = Invoke-WebRequest `
                -Uri "$KongUrl/v1/llm/groq/gpt-oss-120b" `
                -Method Post `
                -Body $groqBody `
                -ContentType "application/json" `
                -Headers @{"X-Tenant-Id" = "test-tenant"} `
                -ErrorAction Stop `
                -TimeoutSec 30
            
            Write-Host " ✓ Authenticated successfully" -ForegroundColor Green
        } catch {
            $statusCode = $_.Exception.Response.StatusCode.value__
            if ($statusCode -eq 401) {
                Write-Host " ✗ Authentication failed (401 - check API key)" -ForegroundColor Red
            } else {
                Write-Host " ⚠ Request failed with status $statusCode" -ForegroundColor Yellow
            }
        }
    }
    
    Write-Host ""
}

# Check logs for sensitive data leakage
Write-Host "5. Checking for sensitive data in logs..." -ForegroundColor Yellow

try {
    # Get recent Kong logs
    $logOutput = docker logs kong-gateway-kong-1 --tail 100 2>&1 | Out-String
    
    $leakedSecrets = @()
    
    # Check for API key patterns in logs
    if ($logOutput -match "sk-proj-\w+") {
        $leakedSecrets += "OpenAI API key pattern found in logs!"
    }
    if ($logOutput -match "sk-ant-\w+") {
        $leakedSecrets += "Anthropic API key pattern found in logs!"
    }
    if ($logOutput -match "AIza[\w-]+") {
        $leakedSecrets += "Google API key pattern found in logs!"
    }
    if ($logOutput -match "gsk_\w+") {
        $leakedSecrets += "Groq API key pattern found in logs!"
    }
    
    if ($leakedSecrets.Count -eq 0) {
        Write-Host "✓ No API keys found in recent logs" -ForegroundColor Green
    } else {
        Write-Host "✗ Potential secret leakage detected:" -ForegroundColor Red
        foreach ($leak in $leakedSecrets) {
            Write-Host "  - $leak" -ForegroundColor Red
        }
        Write-Host "⚠ This is a security issue! Keys should be redacted from logs." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Could not check Docker logs (container might not be running)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Authentication Testing Complete ===" -ForegroundColor Cyan

