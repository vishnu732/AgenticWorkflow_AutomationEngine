import json
from typing import Dict, Any, List, Optional

from sqlalchemy.orm import Session

from app.database.models import WorkflowRun


def save_workflow_run(db: Session, workflow_result: Dict[str, Any]) -> WorkflowRun:
    workflow_run = WorkflowRun(
        workflow_id=workflow_result["workflow_id"],
        original_process=workflow_result["original_process"],
        status=workflow_result["status"],
        steps_json=json.dumps(workflow_result["steps"]),
        audit_log_json=json.dumps(workflow_result["audit_log"]),
    )

    db.add(workflow_run)
    db.commit()
    db.refresh(workflow_run)

    return workflow_run


def get_all_workflow_runs(db: Session) -> List[WorkflowRun]:
    return (
        db.query(WorkflowRun)
        .order_by(WorkflowRun.created_at.desc())
        .all()
    )


def get_workflow_run_by_id(db: Session, workflow_id: str) -> Optional[WorkflowRun]:
    return (
        db.query(WorkflowRun)
        .filter(WorkflowRun.workflow_id == workflow_id)
        .first()
    )


def format_workflow_run(workflow_run: WorkflowRun) -> Dict[str, Any]:
    return {
        "id": workflow_run.id,
        "workflow_id": workflow_run.workflow_id,
        "original_process": workflow_run.original_process,
        "status": workflow_run.status,
        "steps": json.loads(workflow_run.steps_json),
        "audit_log": json.loads(workflow_run.audit_log_json),
        "created_at": workflow_run.created_at.isoformat(),
    }


def format_workflow_summary(workflow_run: WorkflowRun) -> Dict[str, Any]:
    steps = json.loads(workflow_run.steps_json)

    return {
        "id": workflow_run.id,
        "workflow_id": workflow_run.workflow_id,
        "original_process": workflow_run.original_process,
        "status": workflow_run.status,
        "step_count": len(steps),
        "created_at": workflow_run.created_at.isoformat(),
    }