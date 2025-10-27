"""
Tool registry for managing available tools
"""


from src.domain.tools.schemas import ToolMetadata


class ToolRegistry:
    """
    In-memory registry for tools (R1 implementation)
    """

    def __init__(self):
        self._tools: dict[str, ToolMetadata] = {}

    def register_tool(self, tool: ToolMetadata) -> None:
        """
        Register a tool in the registry

        Args:
            tool: Tool metadata to register
        """
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> ToolMetadata | None:
        """
        Get tool metadata by name

        Args:
            name: Tool name

        Returns:
            Tool metadata or None if not found
        """
        return self._tools.get(name)

    def list_tools(self) -> list[ToolMetadata]:
        """
        List all registered tools

        Returns:
            List of all tool metadata
        """
        return list(self._tools.values())

    def unregister_tool(self, name: str) -> bool:
        """
        Unregister a tool from the registry

        Args:
            name: Tool name

        Returns:
            True if tool was removed, False if not found
        """
        if name in self._tools:
            del self._tools[name]
            return True
        return False
