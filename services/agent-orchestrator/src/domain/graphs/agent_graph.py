"""
LangGraph agent execution graph with plan/act/review nodes
"""

from typing import Any, TypedDict

from langgraph.graph import END, Graph


class AgentState(TypedDict):
    """State schema for agent execution"""
    messages: list[dict[str, Any]]
    plan: str | None
    actions: list[dict[str, Any]]
    results: list[dict[str, Any]]
    review: str | None
    next_step: str
    iteration: int


def plan_node(state: AgentState) -> AgentState:
    """
    Planning node: Analyze input and create execution plan

    For R1/AO-002 AC: Echo implementation
    """
    messages = state.get("messages", [])

    plan = f"Echo plan: Will echo {len(messages)} message(s)"

    return {
        **state,
        "plan": plan,
        "next_step": "act"
    }


def act_node(state: AgentState) -> AgentState:
    """
    Action node: Execute the plan

    For R1/AO-002 AC: Echo implementation
    """
    messages = state.get("messages", [])
    actions = state.get("actions", [])
    results = state.get("results", [])

    action = {
        "type": "echo",
        "input": messages
    }
    actions.append(action)

    result = {
        "type": "echo",
        "output": messages,
        "status": "success"
    }
    results.append(result)

    return {
        **state,
        "actions": actions,
        "results": results,
        "next_step": "review"
    }


def review_node(state: AgentState) -> AgentState:
    """
    Review node: Evaluate results and determine if complete

    For R1/AO-002 AC: Echo implementation
    """
    results = state.get("results", [])
    iteration = state.get("iteration", 0)

    review = f"Review: Successfully processed {len(results)} action(s). Iteration {iteration + 1} complete."

    return {
        **state,
        "review": review,
        "next_step": "end",
        "iteration": iteration + 1
    }


def should_continue(state: AgentState) -> str:
    """
    Conditional edge: Determine next step
    """
    next_step = state.get("next_step", "end")

    if next_step == "act":
        return "act"
    elif next_step == "review":
        return "review"
    else:
        return "end"


def create_agent_graph() -> Graph:
    """
    Create the agent execution graph with plan → act → review flow
    """
    workflow = Graph()

    workflow.add_node("plan", plan_node)
    workflow.add_node("act", act_node)
    workflow.add_node("review", review_node)

    workflow.set_entry_point("plan")

    workflow.add_conditional_edges(
        "plan",
        should_continue,
        {
            "act": "act",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        "act",
        should_continue,
        {
            "review": "review",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        "review",
        should_continue,
        {
            "plan": "plan",
            "end": END
        }
    )

    return workflow.compile()
