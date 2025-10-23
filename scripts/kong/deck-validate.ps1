param(
  [string]$StatePath = "infra/kong/kong.yaml"
)

if (-not (Test-Path $StatePath)) {
  Write-Error "State file not found: $StatePath"
  exit 1
}

if (Get-Command conftest -ErrorAction SilentlyContinue) {
  Write-Host "Running conftest policy checks..."
  conftest test $StatePath -p "infra/policies" --combine
} else {
  Write-Host "conftest not found. Skipping policy checks."
}

if (Get-Command deck -ErrorAction SilentlyContinue) {
  Write-Host "Running decK diff (non-blocking if Kong not reachable)..."
  deck diff --state "$StatePath" --non-zero-exit-code
} else {
  Write-Host "decK not found. Skipping decK diff."
}


