import uuid
from typing import List, Dict, Any, Tuple, Callable

from app.agent.ai_decomposer import ai_decompose_process
from app.tools.mock_tools import (
    check_customer_record,
    validate_refund_policy,
    create_support_ticket,
    update_crm_status,
    send_email,
    fallback_tool,
)


def fallback_decompose_process(process_description: str) -> List[Dict[str, Any]]:
    """
    Rule-based fallback decomposition.
    Used if Gemini API fails or API key is missing.
    """

    description = process_description.lower()
    tasks = []

    if "customer" in description or "record" in description:
        tasks.append({
            "task": "Check customer record",
            "tool_hint": "check_customer_record",
            "priority": "medium"
        })

    if "refund" in description or "eligible" in description or "policy" in description:
        tasks.append({
            "task": "Validate refund policy",
            "tool_hint": "validate_refund_policy",
            "priority": "high"
        })

    if "ticket" in description or "support" in description:
        tasks.append({
            "task": "Create support ticket",
            "tool_hint": "create_support_ticket",
            "priority": "medium"
        })

    if "crm" in description or "status" in description:
        tasks.append({
            "task": "Update CRM status",
            "tool_hint": "update_crm_status",
            "priority": "medium"
        })

    if "email" in description or "notify" in description or "confirmation" in description:
        tasks.append({
            "task": "Send confirmation email",
            "tool_hint": "send_email",
            "priority": "medium"
        })

    if not tasks:
        tasks.append({
            "task": "Analyze business process and identify required action",
            "tool_hint": "fallback_tool",
            "priority": "low"
        })

    return tasks


def select_tool(tool_hint: str) -> Tuple[str, Callable]:
    """
    Routes each AI-selected tool hint to the correct mock tool.
    """

    tool_map = {
        "check_customer_record": check_customer_record,
        "validate_refund_policy": validate_refund_policy,
        "create_support_ticket": create_support_ticket,
        "update_crm_status": update_crm_status,
        "send_email": send_email,
        "fallback_tool": fallback_tool,
    }

    tool_function = tool_map.get(tool_hint, fallback_tool)
    tool_name = tool_hint if tool_hint in tool_map else "fallback_tool"

    return tool_name, tool_function


def execute_workflow(process_description: str) -> Dict[str, Any]:
    """
    Executes a full workflow:
    1. AI decomposes process into tasks
    2. Agent selects tools
    3. Tools execute tasks
    4. Audit logs are generated
    """

    workflow_id = str(uuid.uuid4())
    audit_log = []

    audit_log.append(f"Workflow {workflow_id} started.")
    audit_log.append(f"Original process: {process_description}")

    try:
        tasks = ai_decompose_process(process_description)
        decomposition_method = "Gemini + LangChain"
        audit_log.append("Agent used Gemini + LangChain for task decomposition.")

    except Exception as error:
        tasks = fallback_decompose_process(process_description)
        decomposition_method = "Rule-based fallback"
        audit_log.append(f"AI decomposition failed. Fallback used. Reason: {str(error)}")

    audit_log.append(f"Agent decomposed process into {len(tasks)} task(s).")

    steps = []

    for index, task_item in enumerate(tasks, start=1):
        task = task_item["task"]
        tool_hint = task_item["tool_hint"]
        priority = task_item.get("priority", "medium")

        tool_name, tool_function = select_tool(tool_hint)

        audit_log.append(
            f"Step {index}: Selected tool '{tool_name}' for task '{task}' with priority '{priority}'."
        )

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
            "result": {
                **result,
                "priority": priority,
                "decomposition_method": decomposition_method
            }
        })

    final_status = "completed" if all(step["status"] == "completed" for step in steps) else "partial_failure"

    audit_log.append(f"Workflow {workflow_id} finished with status: {final_status}.")

    return {
         "workflow_id": workflow_id,
    "original_process": process_description,
    "status": final_status,
    "steps": steps,
    "audit_log": audit_log,
    "review_status": "pending",
    "human_override": False,
    "override_reason": None
    }