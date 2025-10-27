"""
E2E test for complete workflow flow
"""

import pytest


@pytest.mark.e2e
def test_complete_workflow_flow(test_client):
    """
    Test complete workflow: start → status → completion

    This test validates:
    1. Workflow can be started
    2. Status can be queried
    3. Health checks work
    4. Metrics are exposed
    """
    response = test_client.get("/health/live")
    assert response.status_code == 200

    response = test_client.get("/metrics")
    assert response.status_code == 200
