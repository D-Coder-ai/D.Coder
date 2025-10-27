"""
MCP client for tool discovery and invocation
"""

from src.domain.tools.schemas import ToolInvocationRequest, ToolInvocationResponse, ToolMetadata


class MCPClient:
    """
    Client for Model Context Protocol (MCP) tool integration

    R1: Stub implementation for interfaces
    """

    def __init__(self):
        pass

    async def discover_tools(self) -> list[ToolMetadata]:
        """
        Discover available tools via MCP

        Returns:
            List of tool metadata
        """
        return []

    async def invoke_tool(self, request: ToolInvocationRequest) -> ToolInvocationResponse:
        """
        Invoke a tool via MCP

        Args:
            request: Tool invocation request

        Returns:
            Tool invocation response
        """
        return ToolInvocationResponse(
            tool_name=request.tool_name,
            status="not_implemented",
            error="MCP tool invocation not yet implemented"
        )
