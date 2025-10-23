param(
  [string]$StatePath = "infra/kong/kong.yaml"
)

Write-Host "=== Kong Configuration Validation ===" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $StatePath)) {
  Write-Error "State file not found: $StatePath"
  exit 1
}

# Validate LLM Route Conventions
Write-Host "1. Validating LLM route conventions..." -ForegroundColor Yellow

$yamlContent = Get-Content $StatePath -Raw
$validationErrors = @()
$routeCount = 0
$providers = @("openai", "anthropic", "google", "groq")

# Parse routes from YAML
$routeMatches = Select-String -InputObject $yamlContent -Pattern '- name: (llm\.\w+\.\S+)' -AllMatches

foreach ($match in $routeMatches.Matches) {
    $routeName = $match.Groups[1].Value
    $routeCount++
    
    # Validate naming convention: llm.{provider}.{model}
    if ($routeName -notmatch '^llm\.(openai|anthropic|google|groq)\.[a-z0-9-]+$') {
        $validationErrors += "Route '$routeName' does not follow naming convention llm.{provider}.{model}"
    }
    
    # Extract provider
    $provider = $routeName -replace '^llm\.([^.]+)\..*$', '$1'
    
    # Validate provider is in allowlist
    if ($provider -notin $providers) {
        $validationErrors += "Route '$routeName' uses non-allowlisted provider: $provider"
    }
}

# Check for path patterns
$pathMatches = Select-String -InputObject $yamlContent -Pattern 'paths: \[(/v1/llm/\w+/[^\]]+)\]' -AllMatches

foreach ($match in $pathMatches.Matches) {
    $path = $match.Groups[1].Value
    
    # Validate path pattern: /v1/llm/{provider}/{model}
    if ($path -notmatch '^/v1/llm/(openai|anthropic|google|groq)/[a-z0-9-]+$') {
        $validationErrors += "Path '$path' does not follow pattern /v1/llm/{provider}/{model}"
    }
}

# Validate authentication headers are configured
Write-Host "2. Validating authentication configuration..." -ForegroundColor Yellow

$authValidationErrors = @()
$expectedAuthHeaders = @{
    "openai" = "Authorization: Bearer"
    "anthropic" = "x-api-key:"
    "google" = "x-goog-api-key:"
    "groq" = "Authorization: Bearer"
}

# Parse the YAML to check for auth headers in request-transformer plugins
foreach ($provider in $providers) {
    # Find service section for this provider
    $servicePattern = "- name: $provider"
    $serviceIndex = $yamlContent.IndexOf($servicePattern)
    
    if ($serviceIndex -ge 0) {
        # Look for routes under this service
        $nextServiceIndex = $yamlContent.IndexOf("- name:", $serviceIndex + 1)
        if ($nextServiceIndex -eq -1) { $nextServiceIndex = $yamlContent.Length }
        
        $serviceSection = $yamlContent.Substring($serviceIndex, $nextServiceIndex - $serviceIndex)
        $routesInService = [regex]::Matches($serviceSection, "- name: llm\.$provider\.\S+")
        
        foreach ($routeMatch in $routesInService) {
            $routeName = $routeMatch.Value -replace "- name: ", ""
            
            # Check if this route has the expected auth header
            $routeIndex = $serviceSection.IndexOf($routeMatch.Value)
            $nextRouteIndex = $serviceSection.IndexOf("- name: llm.", $routeIndex + 1)
            if ($nextRouteIndex -eq -1) { $nextRouteIndex = $serviceSection.Length }
            
            $routeSection = $serviceSection.Substring($routeIndex, $nextRouteIndex - $routeIndex)
            
            $expectedHeader = $expectedAuthHeaders[$provider]
            if ($routeSection -notmatch [regex]::Escape($expectedHeader)) {
                $authValidationErrors += "Route '$routeName' missing expected auth header: $expectedHeader"
            }
        }
    }
}

# Report validation results
if ($validationErrors.Count -eq 0 -and $routeCount -gt 0) {
    Write-Host "✓ Found $routeCount LLM routes" -ForegroundColor Green
    Write-Host "✓ All routes follow naming conventions" -ForegroundColor Green
    Write-Host "✓ All paths follow required pattern" -ForegroundColor Green
    Write-Host "✓ All providers are allowlisted" -ForegroundColor Green
} elseif ($routeCount -eq 0) {
    Write-Host "⚠ No LLM routes found in configuration" -ForegroundColor Yellow
} else {
    Write-Host "✗ Route validation failed with $($validationErrors.Count) error(s):" -ForegroundColor Red
    foreach ($validationError in $validationErrors) {
        Write-Host "  - $validationError" -ForegroundColor Red
    }
    exit 1
}

if ($authValidationErrors.Count -eq 0 -and $routeCount -gt 0) {
    Write-Host "✓ All routes have authentication headers configured" -ForegroundColor Green
} elseif ($authValidationErrors.Count -gt 0) {
    Write-Host "✗ Authentication validation failed with $($authValidationErrors.Count) error(s):" -ForegroundColor Red
    foreach ($authError in $authValidationErrors) {
        Write-Host "  - $authError" -ForegroundColor Red
    }
    exit 1
}

Write-Host ""

if (Get-Command conftest -ErrorAction SilentlyContinue) {
  Write-Host "Running conftest policy checks..."
  # Test the combined file that includes both services and allowed_hosts
  conftest test "infra/kong/kong-with-allowlist.yaml" -p "infra/policies" --all-namespaces
  if ($LASTEXITCODE -ne 0) {
    Write-Error "Conftest policy validation failed!"
    exit 1
  }
  Write-Host "✅ Policy validation passed - all hosts are allowlisted"
} else {
  Write-Host "conftest not found. Skipping policy checks."
}

if (Get-Command deck -ErrorAction SilentlyContinue) {
  Write-Host "Running decK gateway diff (skips if Admin API not reachable)..."
  $deckOutput = deck gateway diff "$StatePath" 2>&1
  if ($LASTEXITCODE -ne 0) {
    if ($deckOutput -match "connectex|connection refused|No connection") {
      Write-Warning "Kong Admin API not reachable. Skipping diff (Kong likely not running)."
    } else {
      Write-Error "decK diff failed: $deckOutput"
      exit 1
    }
  } else {
    Write-Host "decK diff successful (no changes detected)."
  }
} else {
  Write-Host "decK not found. Skipping decK diff."
}


