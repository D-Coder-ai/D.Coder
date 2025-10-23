param(
  [string]$StatePath = "infra/kong/kong.yaml"
)

if (-not (Test-Path $StatePath)) {
  Write-Error "State file not found: $StatePath"
  exit 1
}

if (Get-Command conftest -ErrorAction SilentlyContinue) {
  Write-Host "Running conftest policy checks..."
  # Test the combined file that includes both services and allowed_hosts
  conftest test "infra/kong/kong-with-allowlist.yaml" -p "infra/policies"
  if ($LASTEXITCODE -ne 0) {
    Write-Error "Conftest policy validation failed!"
    exit 1
  }
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


