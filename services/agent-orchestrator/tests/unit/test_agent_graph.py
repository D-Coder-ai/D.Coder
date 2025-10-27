"""
Unit tests for agent graph nodes
"""

from src.domain.graphs.agent_graph import (
    AgentState,
    act_node,
    create_agent_graph,
    plan_node,
    review_node,
    should_continue,
)


def test_plan_node():
    """Test plan node execution"""
    initial_state: AgentState = {
        "messages": [{"role": "user", "content": "Hello"}],
        "plan": None,
        "actions": [],
        "results": [],
        "review": None,
        "next_step": "plan",
        "iteration": 0
    }

    result = plan_node(initial_state)

    assert result["plan"] is not None
    assert "echo" in result["plan"].lower()
    assert result["next_step"] == "act"


def test_act_node():
    """Test act node execution"""
    initial_state: AgentState = {
        "messages": [{"role": "user", "content": "Hello"}],
        "plan": "Echo plan",
        "actions": [],
        "results": [],
        "review": None,
        "next_step": "act",
        "iteration": 0
    }

    result = act_node(initial_state)

    assert len(result["actions"]) == 1
    assert len(result["results"]) == 1
    assert result["results"][0]["status"] == "success"
    assert result["next_step"] == "review"


def test_review_node():
    """Test review node execution"""
    initial_state: AgentState = {
        "messages": [{"role": "user", "content": "Hello"}],
        "plan": "Echo plan",
        "actions": [{"type": "echo"}],
        "results": [{"type": "echo", "status": "success"}],
        "review": None,
        "next_step": "review",
        "iteration": 0
    }

    result = review_node(initial_state)

    assert result["review"] is not None
    assert result["next_step"] == "end"
    assert result["iteration"] == 1


def test_should_continue():
    """Test conditional routing"""
    state_act: AgentState = {
        "messages": [],
        "plan": None,
        "actions": [],
        "results": [],
        "review": None,
        "next_step": "act",
        "iteration": 0
    }

    assert should_continue(state_act) == "act"

    state_review: AgentState = {**state_act, "next_step": "review"}
    assert should_continue(state_review) == "review"

    state_end: AgentState = {**state_act, "next_step": "end"}
    assert should_continue(state_end) == "end"


def test_create_agent_graph():
    """Test graph creation"""
    graph = create_agent_graph()

    assert graph is not None
