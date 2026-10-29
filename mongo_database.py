import hmac

from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash

client = MongoClient("mongodb://localhost:27017/")
db = client["hr_leave_system"]

employees_collection = db["employees"]
leave_requests_collection = db["leave_requests"]
users_collection = db["users"]

def add_employee(employee_id, name, department, leave_balance, supervisor):
    employees_collection.update_one(
        {"employee_id": int(employee_id)},
        {"$set": {
            "employee_id": int(employee_id),
            "name": name,
            "department": department,
            "leave_balance": int(leave_balance),
            "supervisor": supervisor
        }},
        upsert=True
    )


def get_employee(employee_id):
    return employees_collection.find_one({"employee_id": int(employee_id)})


def get_all_employees():
    records = employees_collection.find().sort("employee_id", 1)
    return [
        {
            "employee_id": r.get("employee_id", ""),
            "name": r.get("name", ""),
            "department": r.get("department", ""),
            "leave_balance": r.get("leave_balance", ""),
            "supervisor": r.get("supervisor", "")
        }
        for r in records
    ]


def delete_employee(employee_id):
    employees_collection.delete_one({"employee_id": int(employee_id)})


def add_user(username, password, role, name, employee_id=None, supervisor_name=None):
    users_collection.update_one(
        {"username": username},
        {"$set": {
            "username": username,
            "password": generate_password_hash(password),  # only the hash is stored, never the password
            "role": role,          # employee / supervisor / hr
            "name": name,
            "employee_id": employee_id,
            "supervisor_name": supervisor_name
        }},
        upsert=True
    )


def authenticate_user(username, password):
    """The user document when the password is right, else None.

    Accounts created before passwords were hashed still hold plain text; they are accepted once and
    upgraded to a hash on that first successful login.
    """
    if not isinstance(username, str) or not isinstance(password, str):
        return None
    user = users_collection.find_one({"username": username})
    if not user:
        return None
    stored = user.get("password") or ""
    if stored.startswith(("scrypt:", "pbkdf2:")):
        return user if check_password_hash(stored, password) else None
    if hmac.compare_digest(stored.encode(), password.encode()):
        users_collection.update_one({"_id": user["_id"]}, {"$set": {"password": generate_password_hash(password)}})
        return user
    return None


def save_leave_request(employee_id, employee_name, department, leave_type, days, reason, status, recommendation, explanation):
    employee = employees_collection.find_one({"employee_id": int(employee_id)})
    old_balance = int(employee.get("leave_balance", 0)) if employee else 0
    supervisor = employee.get("supervisor", "HR") if employee else "HR"

    leave_requests_collection.insert_one({
        "employee_id": int(employee_id),
        "employee_name": employee_name,
        "department": department,
        "supervisor": supervisor,
        "leave_type": leave_type,
        "days": int(days),
        "reason": reason,
        "status": status,
        "recommendation": recommendation,
        "explanation": explanation,
        "old_balance": old_balance,
        "remaining_balance": old_balance,  # Final HR approval par update hoga
        "created_at": datetime.now(),
        "supervisor_decision_by": "",
        "supervisor_decision_at": None,
        "hr_decision_by": "",
        "hr_decision_at": None
    })


def _request_to_dict(r):
    return {
        "id": str(r.get("_id", "")),
        "employee_id": r.get("employee_id", ""),
        "employee_name": r.get("employee_name", ""),
        "department": r.get("department", ""),
        "supervisor": r.get("supervisor", ""),
        "leave_type": r.get("leave_type", ""),
        "days": r.get("days", ""),
        "reason": r.get("reason", ""),
        "status": r.get("status", ""),
        "recommendation": r.get("recommendation", ""),
        "explanation": r.get("explanation", ""),
        "old_balance": r.get("old_balance", ""),
        "remaining_balance": r.get("remaining_balance", ""),
        "created_at": r.get("created_at", ""),
        "supervisor_decision_by": r.get("supervisor_decision_by", ""),
        "hr_decision_by": r.get("hr_decision_by", "")
    }


def get_all_requests():
    records = leave_requests_collection.find().sort("created_at", -1)
    return [_request_to_dict(r) for r in records]


def get_requests_for_employee(employee_id):
    records = leave_requests_collection.find({"employee_id": int(employee_id)}).sort("created_at", -1)
    return [_request_to_dict(r) for r in records]


def get_requests_for_supervisor(supervisor_name):
    records = leave_requests_collection.find({
        "supervisor": supervisor_name,
        "status": "Pending Supervisor Review"
    }).sort("created_at", -1)
    return [_request_to_dict(r) for r in records]


def supervisor_decision(request_id, decision, decided_by):
    if decision == "recommend":
        new_status = "Recommended by Supervisor"
    else:
        new_status = "Rejected by Supervisor"

    leave_requests_collection.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": {
            "status": new_status,
            "supervisor_decision_by": decided_by,
            "supervisor_decision_at": datetime.now()
        }}
    )


def get_pending_hr_requests():
    records = leave_requests_collection.find({
        "status": {"$in": ["Recommended by Supervisor", "Rejected by Supervisor"]}
    }).sort("created_at", -1)
    return [_request_to_dict(r) for r in records]


def hr_final_decision(request_id, decision, decided_by):
    request_doc = leave_requests_collection.find_one({"_id": ObjectId(request_id)})
    if not request_doc:
        return

    old_balance = int(request_doc.get("old_balance", 0))
    days = int(request_doc.get("days", 0))

    if decision == "accept":
        final_status = "Accepted by HR"
        remaining_balance = max(old_balance - days, 0)
        employees_collection.update_one(
            {"employee_id": int(request_doc["employee_id"])},
            {"$set": {"leave_balance": remaining_balance}}
        )
    else:
        final_status = "Rejected by HR"
        remaining_balance = old_balance

    leave_requests_collection.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": {
            "status": final_status,
            "remaining_balance": remaining_balance,
            "hr_decision_by": decided_by,
            "hr_decision_at": datetime.now()
        }}
    )


def get_analytics_data():
    total_employees = employees_collection.count_documents({})
    total_requests = leave_requests_collection.count_documents({})
    accepted = leave_requests_collection.count_documents({"status": "Accepted by HR"})
    rejected = leave_requests_collection.count_documents({"status": {"$in": ["Rejected by HR", "Rejected by Supervisor"]}})
    pending = leave_requests_collection.count_documents({"status": {"$in": ["Pending Supervisor Review", "Recommended by Supervisor"]}})

    dept_pipeline = [
        {"$group": {"_id": "$department", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    departments = list(leave_requests_collection.aggregate(dept_pipeline))

    leave_type_pipeline = [
        {"$group": {"_id": "$leave_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    leave_types = list(leave_requests_collection.aggregate(leave_type_pipeline))

    return {
        "total_employees": total_employees,
        "total_requests": total_requests,
        "accepted": accepted,
        "rejected": rejected,
        "pending": pending,
        "departments": departments,
        "leave_types": leave_types
    }
