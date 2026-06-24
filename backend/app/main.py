from typing import List, Dict, Any

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.agent.executor import execute_workflow
from app.database.crud import (
    format_workflow_run,
    format_workflow_summary,
    get_all_workflow_runs,
    get_workflow_run_by_id,
    save_workflow_run,
    update_workflow_review,
)
from app.database.db import get_db, init_db
from app.models.schemas import WorkflowRequest, WorkflowResponse, ReviewRequest


app = FastAPI(
    title="Agentic Workflow Automation Engine",
    description="AI-powered workflow automation engine for decomposing business processes into executable tool-based tasks.",
    version="0.3.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {
        "message": "Agentic Workflow Automation Engine API is running."
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "backend",
        "version": "0.3.0"
    }


@app.post("/api/workflows/run", response_model=WorkflowResponse)
def run_workflow(
    request: WorkflowRequest,
    db: Session = Depends(get_db)
):
    result = execute_workflow(request.process_description)

    save_workflow_run(db, result)

    return result


@app.get("/api/workflows", response_model=List[Dict[str, Any]])
def list_workflows(db: Session = Depends(get_db)):
    workflow_runs = get_all_workflow_runs(db)

    return [
        format_workflow_summary(workflow_run)
        for workflow_run in workflow_runs
    ]


@app.get("/api/workflows/{workflow_id}", response_model=Dict[str, Any])
def get_workflow(
    workflow_id: str,
    db: Session = Depends(get_db)
):
    workflow_run = get_workflow_run_by_id(db, workflow_id)

    if not workflow_run:
        raise HTTPException(
            status_code=404,
            detail="Workflow run not found"
        )

    return format_workflow_run(workflow_run)


@app.patch("/api/workflows/{workflow_id}/review", response_model=Dict[str, Any])
def review_workflow(
    workflow_id: str,
    request: ReviewRequest,
    db: Session = Depends(get_db)
):
    workflow_run = update_workflow_review(
        db=db,
        workflow_id=workflow_id,
        review_status=request.review_status,
        override_reason=request.override_reason
    )

    if not workflow_run:
        raise HTTPException(
            status_code=404,
            detail="Workflow run not found"
        )

    return format_workflow_run(workflow_run)


@app.post("/api/workflows/{workflow_id}/retry", response_model=WorkflowResponse)
def retry_workflow(
    workflow_id: str,
    db: Session = Depends(get_db)
):
    existing_workflow = get_workflow_run_by_id(db, workflow_id)

    if not existing_workflow:
        raise HTTPException(
            status_code=404,
            detail="Workflow run not found"
        )

    result = execute_workflow(existing_workflow.original_process)

    result["audit_log"].insert(
        0,
        f"Retry created from original workflow: {workflow_id}."
    )

    save_workflow_run(db, result)

    return result