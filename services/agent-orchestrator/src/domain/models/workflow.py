"""
Workflow domain models
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowInput(BaseModel):
    """Input data for workflow"""
    messages: list[dict[str, Any]] | None = Field(default_factory=list)
    context: dict[str, Any] | None = Field(default_factory=dict)


class WorkflowStartRequest(BaseModel):
    """Request to start a workflow"""
    input: dict[str, Any] = Field(..., description="Input data for the workflow")
    options: dict[str, Any] | None = Field(default=None, description="Workflow options (workflowType, ttlSec, etc.)")


class WorkflowStartResponse(BaseModel):
    """Response after starting a workflow"""
    workflowId: str = Field(..., description="Unique workflow ID")
    runId: str = Field(..., description="Unique run ID for this execution")


class WorkflowStepMetadata(BaseModel):
    """Metadata for a workflow step"""
    stepId: str
    stepType: str
    status: WorkflowStatus
    startedAt: datetime | None = None
    completedAt: datetime | None = None
    result: dict[str, Any] | None = None
    error: str | None = None


class WorkflowMetadata(BaseModel):
    """Complete workflow metadata"""
    workflowId: str
    runId: str
    status: WorkflowStatus
    startedAt: datetime | None = None
    completedAt: datetime | None = None
    result: dict[str, Any] | None = None
    steps: list[WorkflowStepMetadata] = Field(default_factory=list)


class WorkflowStatusResponse(BaseModel):
    """Response for workflow status query"""
    workflowId: str
    status: WorkflowStatus
    result: dict[str, Any] | None = None
    steps: list[WorkflowStepMetadata] = Field(default_factory=list)


class WorkflowSignalRequest(BaseModel):
    """Request to signal a workflow"""
    type: str = Field(..., description="Signal type")
    payload: dict[str, Any] = Field(..., description="Signal payload")
