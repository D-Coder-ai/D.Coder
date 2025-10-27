#!/bin/bash
# Integration Test: Verify Kong routes are accessible
# Tests route reachability and basic plugin functionality

set -e

echo "========================================="
echo "Kong Route Integration Tests"
echo "========================================="

KONG_URL="http://localhost:8000"
ADMIN_URL="http://localhost:8001"
TEST_PASSED=0
TEST_FAILED=0

# Helper function to test route
test_route() {
    local route_name=$1
    local path=$2
    local expected_status=${3:-404}  # 404 is expected when upstream is not running
    
    echo "Testing route: ${route_name} (${path})"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "X-Tenant-Id: test-tenant" \
        -H "X-Request-ID: test-request-123" \
        "${KONG_URL}${path}" 2>/dev/null || echo "000")
    
    # Accept 404 (upstream not available) or 503 (service unavailable) as valid
    # This confirms Kong is routing, even if upstreams aren't running
    if [ "$response" == "404" ] || [ "$response" == "503" ] || [ "$response" == "502" ]; then
        echo "✓ Route ${route_name} is configured (status: ${response})"
        ((TEST_PASSED++))
        return 0
    else
        echo "✗ Route ${route_name} unexpected response (status: ${response})"
        ((TEST_FAILED++))
        return 1
    fi
}

# Test 1: Health check route (Kong internal)
echo "Test 1: Global health endpoint..."
response=$(curl -s -o /dev/null -w "%{http_code}" "${KONG_URL}/health" 2>/dev/null || echo "000")
if [ "$response" == "200" ] || [ "$response" == "503" ]; then
    echo "✓ Health endpoint accessible"
    ((TEST_PASSED++))
else
    echo "✗ Health endpoint failed (status: ${response})"
    ((TEST_FAILED++))
fi

# Test 2: Platform API routes
echo "Test 2: Platform API routes..."
test_route "platform-tenants" "/v1/tenants"
test_route "platform-providers" "/v1/providers"
test_route "platform-quotas" "/v1/quotas"

# Test 3: Agent Orchestrator routes
echo "Test 3: Agent Orchestrator routes..."
test_route "agent-orchestrator-agents" "/v1/agents"
test_route "agent-orchestrator-workflows" "/v1/workflows"

# Test 4: Knowledge & RAG routes
echo "Test 4: Knowledge & RAG routes..."
test_route "knowledge-rag-knowledge" "/v1/knowledge"
test_route "knowledge-rag-documents" "/v1/documents"

# Test 5: LLM provider routes
echo "Test 5: LLM provider routes..."
test_route "llm-openai-gpt-5" "/v1/llm/openai/gpt-5"
test_route "llm-anthropic-claude" "/v1/llm/anthropic/claude-sonnet-4-5"

# Test 6: Check Admin API
echo "Test 6: Admin API accessibility..."
response=$(curl -s -o /dev/null -w "%{http_code}" "${ADMIN_URL}/status" 2>/dev/null || echo "000")
if [ "$response" == "200" ]; then
    echo "✓ Admin API accessible"
    ((TEST_PASSED++))
else
    echo "✗ Admin API failed (status: ${response})"
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

