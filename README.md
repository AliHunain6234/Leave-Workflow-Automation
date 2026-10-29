# Leave Workflow Automation (IntelliHR)

A leave-management web app where an AI-assisted workflow checks each request against HR policy, a supervisor reviews it, and HR gives the final decision. It is a semester project for the Data Science Tools course (8th semester).

## What it does

1. **An employee applies for leave** (leave type, days, reason).
2. **A LangGraph workflow** (`graph.py`) runs four steps in order:
   1. `validate_employee`: looks the employee up in MongoDB (name, department, balance, supervisor).
   2. `policy_check`: applies the HR rules below.
   3. `ai_recommendation`: asks an OpenAI model (through LangChain) for a short HR recommendation and explanation. If the API is unavailable, a policy-based fallback text is used instead.
   4. `save_request`: stores the request with its status, recommendation and explanation.
3. **The supervisor** sees the pending requests of their team and recommends or rejects each one.
4. **HR** sees what the supervisor decided and gives the final accept or reject. Accepting deducts the days from the employee's leave balance.
5. **HR analytics** show requests per department and per leave type, plus totals (employees, requests, accepted, rejected, pending).

### Policy rules applied automatically

| Rule | Result |
|---|---|
| Employee ID not found | Rejected by HR |
| Days is zero or negative | Rejected by HR |
| Days exceed the leave balance | Rejected by HR |
| Casual leave longer than 3 days in one request | Rejected by HR |
| Sick leave longer than 2 days with no mention of a medical certificate | Rejected by HR |
| Everything else | Pending Supervisor Review |

### Request statuses

`Pending Supervisor Review` -> `Recommended by Supervisor` / `Rejected by Supervisor` -> `Accepted by HR` / `Rejected by HR`

## Roles and pages

| Role | Can do |
|---|---|
| Employee | Apply for leave, see their own request history (`/leave`) |
| Supervisor | Review and decide on their team's requests (`/supervisor-dashboard`) |
| HR | Final decisions (`/hr-dashboard`), analytics (`/analytics`), add and delete employees (`/add-employee`) |

Public pages: home, services, about, contact, login.

## Tech stack

Python, Flask, LangGraph, LangChain + OpenAI (`gpt-4o-mini`), MongoDB (`pymongo`), plain HTML/CSS pages.

## Run it

You need Python 3.10+ and a MongoDB server running on `localhost:27017` (the database name is `hr_leave_system`).

```bash
python -m venv venv
venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file next to `app.py`:

```text
OPENAI_API_KEY=your-openai-key
```

The key is optional: without it the workflow still runs and uses the fallback recommendation text.

```bash
python mongo_seed.py           # WARNING: clears the employees, requests and users collections, then adds 25 employees and 4 demo logins
python app.py                  # http://127.0.0.1:5500
```

The demo accounts (HR, supervisor and two employees) are defined at the bottom of `mongo_seed.py`. `python mongo_test.py` checks the MongoDB connection.

## Project layout

| File | Purpose |
|---|---|
| `app.py` | Flask routes, sessions and role checks |
| `graph.py` | The LangGraph leave workflow |
| `llm.py` | OpenAI client used for the recommendation |
| `mongo_database.py` | All MongoDB reads and writes (employees, users, requests, analytics) |
| `mongo_seed.py`, `mongo_test.py` | Demo data and a connection check |
| `*.html`, `style.css` | The pages and the styling |

## Status and limitations

- This is a **demo-grade** project. Passwords are stored as plain text in MongoDB and the Flask secret key in `app.py` is a placeholder; do not deploy it as it is.
- The MongoDB address is fixed to `localhost` in `mongo_database.py`.
- The AI recommendation is advice only; the policy rules and the human decisions are what change a request's status.
