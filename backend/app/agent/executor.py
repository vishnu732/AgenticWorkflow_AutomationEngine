import uuid
from typing import List, Dict, Any

from app.tools.mock_tools import (
    check_customer_record,
    validate_refund_policy,
    create_support_ticket,
    update_crm_status,
    send_email,
    fallback_tool,
)


def decompose_process(process_description: str) -> List[str]:
    """
    Basic rule-based decomposition for MVP.
    In Step 3, we will replace this with Gemini + LangChain.
    """

    description = process_description.lower()
    tasks = []

    if "customer" in description or "record" in description:
        tasks.append("Check customer record")

    if "refund" in description or "eligible" in description or "policy" in description:
        tasks.append("Validate refund policy")

    if "ticket" in description or "support" in description:
        tasks.append("Create support ticket")

    if "crm" in description or "status" in description:
        tasks.append("Update CRM status")

    if "email" in description or "notify" in description or "confirmation" in description:
        tasks.append("Send confirmation email")

    if not tasks:
        tasks.append("Analyze business process and identify required action")

    return tasks


def select_tool(task: str):
    """
    Routes each task to the correct mock tool.
    """

    task_lower = task.lower()

    if "customer" in task_lower:
        return "check_customer_record", check_customer_record

    if "refund" in task_lower or "policy" in task_lower:
        return "validate_refund_policy", validate_refund_policy

    if "ticket" in task_lower or "support" in task_lower:
        return "create_support_ticket", create_support_ticket

    if "crm" in task_lower or "status" in task_lower:
        return "update_crm_status", update_crm_status

    if "email" in task_lower or "notify" in task_lower:
        return "send_email", send_email

    return "fallback_tool", fallback_tool


def execute_workflow(process_description: str) -> Dict[str, Any]:
    """
    Executes a full workflow:
    1. Decompose process
    2. Select tools
    3. Run tools
    4. Store audit-style logs
    """

    workflow_id = str(uuid.uuid4())
    tasks = decompose_process(process_description)

    steps = []
    audit_log = []

    audit_log.append(f"Workflow {workflow_id} started.")
    audit_log.append(f"Original process: {process_description}")
    audit_log.append(f"Agent decomposed process into {len(tasks)} task(s).")

    for index, task in enumerate(tasks, start=1):
        tool_name, tool_function = select_tool(task)

        audit_log.append(f"Step {index}: Selected tool '{tool_name}' for task '{task}'.")

        try:
            result = tool_function(task)
            status = "completed"
            audit_log.append(f"Step {index}: Task completed successfully.")

        except Exception as error:
            result = {"error": str(error)}
            status = "failed"
            audit_log.append(f"Step {index}: Task failed with error: {str(error)}.")

        steps.append({
            "step_id": index,
            "task": task,
            "tool_used": tool_name,
            "status": status,
            "result": result
        })

    final_status = "completed" if all(step["status"] == "completed" for step in steps) else "partial_failure"

    audit_log.append(f"Workflow {workflow_id} finished with status: {final_status}.")

    return {
        "workflow_id": workflow_id,
        "original_process": process_description,
        "status": final_status,
        "steps": steps,
        "audit_log": audit_log
    }