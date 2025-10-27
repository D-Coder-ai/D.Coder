"""
Integration tests for health endpoints
"""



def test_health_endpoint(test_client):
    """Test /health endpoint"""
    response = test_client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "agent-orchestrator"


def test_ready_endpoint(test_client):
    """Test /health/ready endpoint"""
    response = test_client.get("/health/ready")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_live_endpoint(test_client):
    """Test /health/live endpoint"""
    response = test_client.get("/health/live")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
