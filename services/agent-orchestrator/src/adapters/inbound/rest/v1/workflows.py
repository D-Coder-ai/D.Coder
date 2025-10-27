"""
Workflow Endpoints
"""


from fastapi import APIRouter, HTTPException, Request, status

from src.domain.models.workflow import (
    WorkflowSignalRequest,
    WorkflowStartRequest,
    WorkflowStartResponse,
    WorkflowStatusResponse,
)

router = APIRouter()


@router.post(
    "/start",
    response_model=WorkflowStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start Workflow",
    description="Start a new workflow execution"
)
async def start_workflow(
    request: Request,
    body: WorkflowStartRequest
) -> WorkflowStartResponse:
    """
    Start a new workflow execution
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Workflow execution not yet implemented"
    )


@router.get(
    "/{workflowId}",
    response_model=WorkflowStatusResponse,
    summary="Get Workflow Status",
    description="Get the current status of a workflow"
)
async def get_workflow_status(
    workflowId: str
) -> WorkflowStatusResponse:
    """
    Get the current status of a workflow
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Workflow status query not yet implemented"
    )


@router.post(
    "/{workflowId}/signal",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Signal Workflow",
    description="Send a signal to a running workflow"
)
async def signal_workflow(
    workflowId: str,
    body: WorkflowSignalRequest
) -> dict[str, str]:
    """
    Send a signal to a running workflow
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Workflow signaling not yet implemented"
    )
