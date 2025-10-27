"""
Integration tests for LangGraph service
"""

import pytest

from src.application.services.langgraph_service import LangGraphService


@pytest.mark.asyncio
async def test_execute_echo_graph():
    """Test echo graph execution"""
    service = LangGraphService()

    input_data = {
        "messages": [
            {"role": "user", "content": "Hello, world!"}
        ]
    }

    result = await service.execute_graph(input_data)

    assert result["status"] == "completed"
    assert result["plan"] is not None
    assert len(result["actions"]) > 0
    assert len(result["results"]) > 0
    assert result["review"] is not None
