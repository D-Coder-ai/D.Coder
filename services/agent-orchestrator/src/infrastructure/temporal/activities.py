"""
Temporal activities
"""

from typing import Any

from temporalio import activity

from src.application.services.langgraph_service import LangGraphService


@activity.defn
async def execute_langgraph_step(input_data: dict[str, Any]) -> dict[str, Any]:
    """
    Activity: Execute a LangGraph step

    Args:
        input_data: Input for the LangGraph execution

    Returns:
        Result from LangGraph execution
    """
    service = LangGraphService()
    result = await service.execute_graph(input_data)
    return result


@activity.defn
async def publish_event_activity(event_type: str, event_data: dict[str, Any]) -> None:
    """
    Activity: Publish an event to NATS

    Args:
        event_type: Type of event to publish
        event_data: Event payload data
    """
    pass
