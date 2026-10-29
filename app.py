from flask import Flask, request, render_template_string, redirect, session, url_for, send_from_directory
from graph import leave_graph
from mongo_database import (
    get_all_requests, add_employee, get_all_employees, delete_employee,
    authenticate_user, get_requests_for_employee, get_requests_for_supervisor,
    supervisor_decision, get_pending_hr_requests, hr_final_decision,
    get_analytics_data
)

app = Flask(__name__)
app.secret_key = "change-me-to-a-long-random-secret"  # Demo key. Use ENV secret in production.


def current_user():
    return session.get("user")


def render_page(file_name, result=None, message=None, extra=None):
    with open(file_name, "r", encoding="utf-8") as file:
        html = file.read()

    # Home page par Dashboard option bilkul hide rahega.
    # Logout/Login apni jagah rahega, lekin Dashboard link remove ho jayega.
    if file_name == "home.html":
        html = html.replace('<a href="/dashboard">Dashboard</a>', '')

    user = current_user()
    role = user.get("role") if user else None

    # Role-based data display
    if role == "employee":
        requests = get_requests_for_employee(user.get("employee_id"))
    else:
        requests = get_all_requests()

    employees = get_all_employees()

    context = {
        "result": result,
        "requests": requests,
        "employees": employees,
        "message": message,
        "user": user
    }
    if extra:
        context.update(extra)

    return render_template_string(html, **context)


def login_required(role=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = current_user()
            if not user:
                return redirect("/login")
            if role and user.get("role") != role:
                return redirect("/dashboard")
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator


@app.route("/")
def home():
    return render_page("home.html")


@app.route("/services")
def services():
    return render_page("services.html")


@app.route("/about")
def about():
    return render_page("about.html")

@app.route("/contact")
def contact():
    return render_page("contact.html")


@app.route("/AI Brain.jpg")
def ai_brain_image():
    # Image ko project root se serve karega.
    # Apni picture ka naam exactly "AI Brain.jpg" rakhein.
    return send_from_directory(".", "AI Brain.jpg")


@app.route("/future-bg.jpg")
def future_background_image():
    return send_from_directory(".", "future-bg.jpg")

@app.route("/style.css")
def style():
    with open("style.css", "r", encoding="utf-8") as file:
        return file.read(), 200, {"Content-Type": "text/css"}


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = authenticate_user(username, password)

        if user:
            session["user"] = {
                "username": user.get("username"),
                "role": user.get("role"),
                "name": user.get("name"),
                "employee_id": user.get("employee_id"),
                "supervisor_name": user.get("supervisor_name")
            }
            return redirect("/dashboard")

        return render_page("login.html", message="Invalid username or password.")

    return render_page("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/dashboard")
@login_required()
def dashboard():
    user = current_user()
    if user["role"] == "employee":
        return redirect("/leave")
    if user["role"] == "supervisor":
        return redirect("/supervisor-dashboard")
    if user["role"] == "hr":
        return redirect("/hr-dashboard")
    return render_page("home.html")


@app.route("/leave")
@login_required("employee")
def leave():
    return render_page("leave.html")


@app.route("/apply-leave", methods=["POST"])
@login_required()
def apply_leave():
    user = current_user()

    if user["role"] == "employee":
        employee_id = int(user["employee_id"])
    else:
        employee_id = int(request.form["employee_id"])

    leave_type = request.form["leave_type"]
    days = int(request.form["days"])
    reason = request.form["reason"]

    state = {
        "employee_id": employee_id,
        "leave_type": leave_type,
        "days": days,
        "reason": reason,
        "employee_name": "",
        "department": "",
        "leave_balance": 0,
        "supervisor": "",
        "status": "",
        "recommendation": "",
        "explanation": ""
    }

    result = leave_graph.invoke(state)
    return render_page("leave.html", result=result, message="Leave request submitted successfully.")


@app.route("/supervisor-dashboard")
@login_required("supervisor")
def supervisor_dashboard():
    pending_requests = get_all_requests()
    return render_page("supervisor_dashboard.html", extra={"pending_requests": pending_requests})


@app.route("/supervisor-decision/<request_id>/<decision>", methods=["POST"])
@login_required("supervisor")
def supervisor_decision_route(request_id, decision):
    user = current_user()
    supervisor_decision(request_id, decision, user.get("name"))
    return redirect("/supervisor-dashboard")


@app.route("/hr-dashboard")
@login_required("hr")
def hr_dashboard():
    pending_hr_requests = get_pending_hr_requests()
    return render_page("hr_dashboard.html", extra={"pending_hr_requests": pending_hr_requests})


@app.route("/hr-decision/<request_id>/<decision>", methods=["POST"])
@login_required("hr")
def hr_decision_route(request_id, decision):
    user = current_user()
    hr_final_decision(request_id, decision, user.get("name"))
    return redirect("/hr-dashboard")


@app.route("/analytics")
@login_required("hr")
def analytics():
    analytics_data = get_analytics_data()
    return render_page("analytics.html", extra={"analytics": analytics_data})


@app.route("/add-employee")
@login_required("hr")
def add_employee_page():
    return render_page("add_employee.html")


@app.route("/save-employee", methods=["POST"])
@login_required("hr")
def save_employee():
    employee_id = int(request.form["employee_id"])
    name = request.form["name"]
    department = request.form["department"]
    leave_balance = int(request.form["leave_balance"])
    supervisor = request.form["supervisor"]

    add_employee(employee_id, name, department, leave_balance, supervisor)
    return render_page("add_employee.html", message="Employee added successfully.")


@app.route("/delete-employee/<int:employee_id>", methods=["POST"])
@login_required("hr")
def delete_employee_route(employee_id):
    delete_employee(employee_id)
    return render_page("add_employee.html", message="Employee deleted successfully.")


if __name__ == "__main__":
    app.run(debug=True, port=5500)
