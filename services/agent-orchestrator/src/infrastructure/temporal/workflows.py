"""
Temporal workflow definitions
"""

from datetime import timedelta
from typing import Any

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from src.infrastructure.temporal.activities import (
        execute_langgraph_step,
    )


@workflow.defn
class AgentWorkflow:
    """
    Temporal workflow for agent execution with LangGraph
    """

    @workflow.run
    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the agent workflow

        Args:
            input_data: Input for the workflow

        Returns:
            Final workflow result
        """
        retry_policy = RetryPolicy(
            maximum_attempts=3,
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=10),
            backoff_coefficient=2.0
        )

        result = await workflow.execute_activity(
            execute_langgraph_step,
            input_data,
            start_to_close_timeout=timedelta(seconds=300),
            retry_policy=retry_policy
        )

        return result

    @workflow.signal
    async def external_signal(self, signal_data: dict[str, Any]) -> None:
        """
        Handle external signals to the workflow

        Args:
            signal_data: Signal data from external source
        """
        pass
