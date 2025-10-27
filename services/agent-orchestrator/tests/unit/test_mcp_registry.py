"""
Unit tests for MCP tool registry
"""

from src.adapters.outbound.mcp.registry import ToolRegistry
from src.domain.tools.schemas import ToolMetadata


def test_register_tool():
    """Test tool registration"""
    registry = ToolRegistry()

    tool = ToolMetadata(
        name="test_tool",
        description="A test tool",
        schema={"type": "object"},
        method="POST"
    )

    registry.register_tool(tool)

    retrieved = registry.get_tool("test_tool")
    assert retrieved is not None
    assert retrieved.name == "test_tool"


def test_list_tools():
    """Test listing all tools"""
    registry = ToolRegistry()

    tool1 = ToolMetadata(name="tool1", description="Tool 1", schema={})
    tool2 = ToolMetadata(name="tool2", description="Tool 2", schema={})

    registry.register_tool(tool1)
    registry.register_tool(tool2)

    tools = registry.list_tools()
    assert len(tools) == 2


def test_unregister_tool():
    """Test tool unregistration"""
    registry = ToolRegistry()

    tool = ToolMetadata(name="test_tool", description="Test", schema={})
    registry.register_tool(tool)

    assert registry.unregister_tool("test_tool") is True
    assert registry.get_tool("test_tool") is None
    assert registry.unregister_tool("nonexistent") is False
