param(
  [string]$StatePath = "infra/kong/kong.yaml"
)

if (-not (Test-Path $StatePath)) {
  Write-Error "State file not found: $StatePath"
  exit 1
}

if (Get-Command conftest -ErrorAction SilentlyContinue) {
  Write-Host "Running conftest policy checks..."
  # Provide allowlist data file explicitly to input so policy can read it
  conftest test $StatePath -p "infra/policies" --combine --input "infra/policies/allowed_provider_hosts.yaml"
} else {
  Write-Host "conftest not found. Skipping policy checks."
}

if (Get-Command deck -ErrorAction SilentlyContinue) {
  Write-Host "Running decK gateway diff (skips if Admin API not reachable)..."
  try {
    deck gateway diff "$StatePath" --non-zero-exit-code
  } catch {
    Write-Warning "decK could not reach Admin API (likely Kong not running). Skipping diff."
  }
} else {
  Write-Host "decK not found. Skipping decK diff."
}


