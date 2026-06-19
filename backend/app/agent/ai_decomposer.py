import os
from typing import List, Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()


ToolName = Literal[
    "check_customer_record",
    "validate_refund_policy",
    "create_support_ticket",
    "update_crm_status",
    "send_email",
    "fallback_tool",
]


class AgentTask(BaseModel):
    task: str = Field(description="Clear executable business task")
    tool_hint: ToolName = Field(description="Best tool to execute this task")
    priority: Literal["low", "medium", "high"] = Field(description="Task priority")


class WorkflowPlan(BaseModel):
    tasks: List[AgentTask] = Field(description="Ordered list of executable workflow tasks")


def ai_decompose_process(process_description: str) -> List[dict]:
    """
    Uses Gemini + LangChain structured output to convert a business process
    into ordered executable tasks.
    """

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY is missing. Add it to backend/.env")

    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        max_retries=2,
    )

    structured_model = model.with_structured_output(WorkflowPlan)

    prompt = f"""
You are an enterprise workflow automation planner.

Convert the business process below into ordered executable tasks.

Available tools:
1. check_customer_record - verify customer or account details
2. validate_refund_policy - check refund/policy/business eligibility
3. create_support_ticket - create a support/service ticket
4. update_crm_status - update CRM/order/customer status
5. send_email - send notification or confirmation email
6. fallback_tool - use only when no other tool fits

Rules:
- Return tasks in execution order.
- Each task must be specific and action-oriented.
- Choose the best tool_hint from the available tools.
- Do not include private reasoning.
- Do not create more than 7 tasks.

Business process:
{process_description}
"""

    plan = structured_model.invoke(prompt)

    return [
        {
            "task": item.task,
            "tool_hint": item.tool_hint,
            "priority": item.priority,
        }
        for item in plan.tasks
    ]