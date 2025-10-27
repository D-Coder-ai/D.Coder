#!/bin/bash
# Run all Kong Gateway tests
# Executes unit, integration, and e2e tests

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOTAL_PASSED=0
TOTAL_FAILED=0

echo "========================================"
echo "Kong Gateway R1 Test Suite"
echo "========================================"
echo ""

# Change to service root
cd "${SCRIPT_DIR}/.."

# Make all test scripts executable
chmod +x tests/unit/*.sh
chmod +x tests/integration/*.sh
chmod +x tests/e2e/*.sh

# Run Unit Tests
echo "Running Unit Tests..."
echo "----------------------------------------"
if bash tests/unit/test_config_validation.sh; then
    echo "Unit tests: PASSED"
    ((TOTAL_PASSED++))
else
    echo "Unit tests: FAILED"
    ((TOTAL_FAILED++))
fi
echo ""

# Check if Kong is running for integration/e2e tests
if ! docker-compose ps kong | grep -q "Up"; then
    echo "⚠ WARNING: Kong container not running"
    echo "  Skipping integration and e2e tests"
    echo "  Run: docker-compose up -d"
    echo ""
    exit 0
fi

# Run Integration Tests
echo "Running Integration Tests..."
echo "----------------------------------------"
if bash tests/integration/test_routes.sh; then
    echo "Integration tests: PASSED"
    ((TOTAL_PASSED++))
else
    echo "Integration tests: FAILED"
    ((TOTAL_FAILED++))
fi
echo ""

# Run E2E Tests
echo "Running E2E Tests..."
echo "----------------------------------------"
echo "Rate Limiting Tests:"
if bash tests/e2e/test_rate_limiting.sh; then
    echo "Rate limiting tests: PASSED"
    ((TOTAL_PASSED++))
else
    echo "Rate limiting tests: FAILED"
    ((TOTAL_FAILED++))
fi
echo ""

echo "Headers & Observability Tests:"
if bash tests/e2e/test_headers_and_observability.sh; then
    echo "Headers & observability tests: PASSED"
    ((TOTAL_PASSED++))
else
    echo "Headers & observability tests: FAILED"
    ((TOTAL_FAILED++))
fi
echo ""

# Final Results
echo "========================================"
echo "Final Test Results:"
echo "  Test Suites Passed: ${TOTAL_PASSED}"
echo "  Test Suites Failed: ${TOTAL_FAILED}"
echo "========================================"

if [ ${TOTAL_FAILED} -gt 0 ]; then
    exit 1
fi

echo "✓ All tests passed!"
exit 0

