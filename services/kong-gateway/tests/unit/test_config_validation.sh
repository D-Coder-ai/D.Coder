#!/bin/bash
# Unit Test: Validate Kong declarative configuration files
# Ensures YAML syntax is valid and Kong can parse the configs

set -e

echo "========================================="
echo "Kong Configuration Validation Tests"
echo "========================================="

CONFIG_DIR="$(pwd)/config"
TEST_PASSED=0
TEST_FAILED=0

# Test 1: Validate kong.yml syntax
echo "Test 1: Validating kong.yml..."
if docker run --rm -v "${CONFIG_DIR}:/config" kong:3.8 kong config parse /config/kong.yml > /dev/null 2>&1; then
    echo "✓ kong.yml is valid"
    ((TEST_PASSED++))
else
    echo "✗ kong.yml validation failed"
    ((TEST_FAILED++))
fi

# Test 2: Validate platform-services.yml syntax
echo "Test 2: Validating platform-services.yml..."
if docker run --rm -v "${CONFIG_DIR}/routes:/config" kong:3.8 kong config parse /config/platform-services.yml > /dev/null 2>&1; then
    echo "✓ platform-services.yml is valid"
    ((TEST_PASSED++))
else
    echo "✗ platform-services.yml validation failed"
    ((TEST_FAILED++))
fi

# Test 3: Validate health.yml syntax
echo "Test 3: Validating health.yml..."
if docker run --rm -v "${CONFIG_DIR}/routes:/config" kong:3.8 kong config parse /config/health.yml > /dev/null 2>&1; then
    echo "✓ health.yml is valid"
    ((TEST_PASSED++))
else
    echo "✗ health.yml validation failed"
    ((TEST_FAILED++))
fi

# Test 4: Check merge script exists and is executable
echo "Test 4: Checking merge-configs.sh..."
if [ -x "${CONFIG_DIR}/merge-configs.sh" ]; then
    echo "✓ merge-configs.sh exists and is executable"
    ((TEST_PASSED++))
else
    echo "✗ merge-configs.sh not executable"
    ((TEST_FAILED++))
fi

echo ""
echo "========================================="
echo "Test Results:"
echo "  Passed: ${TEST_PASSED}"
echo "  Failed: ${TEST_FAILED}"
echo "========================================="

if [ ${TEST_FAILED} -gt 0 ]; then
    exit 1
fi

exit 0

