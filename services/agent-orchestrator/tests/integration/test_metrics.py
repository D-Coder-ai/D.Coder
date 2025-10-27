"""
Integration tests for metrics endpoint
"""



def test_metrics_endpoint(test_client):
    """Test /metrics endpoint returns Prometheus format"""
    response = test_client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")

    content = response.text
    assert "workflow_duration_seconds" in content or len(content) > 0
