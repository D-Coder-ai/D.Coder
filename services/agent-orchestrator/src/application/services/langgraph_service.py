"""
LangGraph execution service
"""

from typing import Any

from src.domain.graphs.agent_graph import AgentState, create_agent_graph


class LangGraphService:
    """Service for executing LangGraph workflows"""

    def __init__(self):
        self.graph = create_agent_graph()

    async def execute_graph(
        self,
        input_data: dict[str, Any],
        config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Execute the agent graph with given input

        Args:
            input_data: Input data for the graph
            config: Optional configuration for execution

        Returns:
            Final state after graph execution
        """
        initial_state: AgentState = {
            "messages": input_data.get("messages", []),
            "plan": None,
            "actions": [],
            "results": [],
            "review": None,
            "next_step": "plan",
            "iteration": 0
        }

        try:
            final_state = await self.graph.ainvoke(initial_state, config=config or {})

            return {
                "status": "completed",
                "plan": final_state.get("plan"),
                "actions": final_state.get("actions", []),
                "results": final_state.get("results", []),
                "review": final_state.get("review"),
                "iterations": final_state.get("iteration", 0)
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "plan": None,
                "actions": [],
                "results": [],
                "review": None,
                "iterations": 0
            }
