param(
  [string]$StatePath = "infra/kong/kong.yaml"
)

if (-not (Test-Path $StatePath)) {
  Write-Error "State file not found: $StatePath"
  exit 1
}

if (Get-Command deck -ErrorAction SilentlyContinue) {
  Write-Host "Running decK diff..."
  deck diff --state "$StatePath" --non-zero-exit-code
} else {
  Write-Error "decK not found. Install decK to run diffs: https://docs.konghq.com/deck/"
  exit 1
}


