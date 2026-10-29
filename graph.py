from typing import TypedDict
from langgraph.graph import StateGraph, END
from mongo_database import get_employee, save_leave_request
from llm import llm


class LeaveState(TypedDict):
    employee_id: int
    leave_type: str
    days: int
    reason: str
    employee_name: str
    department: str
    leave_balance: int
    supervisor: str
    status: str
    recommendation: str
    explanation: str


def validate_employee(state: LeaveState):
    employee = get_employee(state["employee_id"])

    if employee is None:
        state["employee_name"] = "Unknown"
        state["department"] = "Unknown"
        state["leave_balance"] = 0
        state["supervisor"] = "HR"
        state["status"] = "Rejected by HR"
        state["recommendation"] = "Employee record not found."
        state["explanation"] = "The entered employee ID does not exist in the employee database."
        return state

    state["employee_name"] = employee["name"]
    state["department"] = employee["department"]
    state["leave_balance"] = employee["leave_balance"]
    state["supervisor"] = employee["supervisor"]
    return state


def policy_check(state: LeaveState):
    if state["status"] == "Rejected by HR":
        return state

    leave_type = state["leave_type"]
    days = int(state["days"])
    balance = int(state["leave_balance"])
    reason = state["reason"].lower()

    if days <= 0:
        state["status"] = "Rejected by HR"
        state["recommendation"] = "Invalid leave duration."
        state["explanation"] = "Leave days must be greater than zero."

    elif days > balance:
        state["status"] = "Rejected by HR"
        state["recommendation"] = "Leave request exceeds available balance."
        state["explanation"] = f"Employee has only {balance} leave days, but requested {days} days."

    elif leave_type == "Casual Leave" and days > 3:
        state["status"] = "Rejected by HR"
        state["recommendation"] = "Casual leave cannot exceed 3 days in one request."
        state["explanation"] = "The request violates the casual leave policy limit."

    elif leave_type == "Sick Leave" and days > 2 and "medical" not in reason and "certificate" not in reason:
        state["status"] = "Rejected by HR"
        state["recommendation"] = "Medical certificate is required for sick leave above 2 days."
        state["explanation"] = "Sick leave above 2 days needs medical proof according to policy."

    else:
        state["status"] = "Pending Supervisor Review"
        state["explanation"] = "Policy check passed. Request is forwarded to supervisor for human review."

    return state


def ai_recommendation(state: LeaveState):
    if state["status"] == "Rejected by HR":
        return state

    prompt = f"""
    You are an HR officer reviewing a leave request.

    Employee: {state['employee_name']}
    Department: {state['department']}
    Supervisor: {state['supervisor']}
    Leave Type: {state['leave_type']}
    Leave Balance: {state['leave_balance']} days
    Requested Leave: {state['days']} days
    Reason: {state['reason']}

    Write two short sections:
    1. Recommendation: professional HR recommendation.
    2. Explanation: clear reason why the request should move forward or needs caution.
    """

    try:
        response = llm.invoke(prompt)
        state["recommendation"] = response.content
    except Exception:
        state["recommendation"] = (
            "AI recommendation could not be generated because the OpenAI API quota is unavailable. "
            "Based on HR policy, the request may proceed because the employee has sufficient leave balance."
        )

    if not state.get("explanation"):
        state["explanation"] = "The request passed basic HR policy checks and requires supervisor review."

    return state


def save_request(state: LeaveState):
    save_leave_request(
        employee_id=state["employee_id"],
        employee_name=state["employee_name"],
        department=state["department"],
        leave_type=state["leave_type"],
        days=state["days"],
        reason=state["reason"],
        status=state["status"],
        recommendation=state["recommendation"],
        explanation=state["explanation"]
    )
    return state


builder = StateGraph(LeaveState)
builder.add_node("validate_employee", validate_employee)
builder.add_node("policy_check", policy_check)
builder.add_node("ai_recommendation", ai_recommendation)
builder.add_node("save_request", save_request)

builder.set_entry_point("validate_employee")
builder.add_edge("validate_employee", "policy_check")
builder.add_edge("policy_check", "ai_recommendation")
builder.add_edge("ai_recommendation", "save_request")
builder.add_edge("save_request", END)

leave_graph = builder.compile()
