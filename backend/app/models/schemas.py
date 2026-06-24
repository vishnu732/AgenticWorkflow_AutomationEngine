from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal


class WorkflowRequest(BaseModel):
    process_description: str = Field(
        ...,
        min_length=10,
        description="Natural language business process description"
    )


class WorkflowStep(BaseModel):
    step_id: int
    task: str
    tool_used: str
    status: str
    result: Dict[str, Any]


class WorkflowResponse(BaseModel):
    workflow_id: str
    original_process: str
    status: str
    steps: List[WorkflowStep]
    audit_log: List[str]
    review_status: str = "pending"
    human_override: bool = False
    override_reason: Optional[str] = None


class ReviewRequest(BaseModel):
    review_status: Literal["approved", "rejected"]
    override_reason: Optional[str] = Field(
        default=None,
        description="Reason provided by human reviewer"
    )