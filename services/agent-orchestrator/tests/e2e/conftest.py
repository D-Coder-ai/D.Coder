"""
E2E test configuration
"""

import pytest


@pytest.fixture(scope="session")
def docker_compose_file():
    """Docker compose file for E2E tests"""
    return "docker-compose.yml"
