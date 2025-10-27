"""
Tool schemas for MCP and HTTP tools
"""

from typing import Any

from pydantic import BaseModel, Field


class ToolMetadata(BaseModel):
    """Metadata for a tool"""
    name: str
    description: str
    schema: dict[str, Any]
    endpoint: str | None = None
    method: str = "POST"


class ToolInvocationRequest(BaseModel):
    """Request to invoke a tool"""
    tool_name: str = Field(..., description="Name of the tool to invoke")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Tool parameters")


class ToolInvocationResponse(BaseModel):
    """Response from tool invocation"""
    tool_name: str
    status: str
    result: dict[str, Any] | None = None
    error: str | None = None
