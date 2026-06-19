from pydantic import BaseModel, Field
from typing import List, Dict, Any


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