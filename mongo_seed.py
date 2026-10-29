import os
import secrets

from dotenv import load_dotenv

from mongo_database import employees_collection,leave_requests_collection, users_collection, add_employee, add_user

# Old data clear
employees_collection.delete_many({})
leave_requests_collection.delete_many({})
users_collection.delete_many({})

# 25 Employees
employees = [
    (1, "Ali Ahmad", "Administration", 10, "Principal"),
    (2, "Sara Khan", "Academics", 8, "Principal"),
    (3, "Usman Tariq", "Hostel", 6, "Principal"),
    (4, "Ayesha Malik", "Finance", 12, "Principal"),
    (5, "Bilal Hassan", "IT Department", 15, "Principal"),
    (6, "Fatima Noor", "Human Resource", 9, "Principal"),
    (7, "Ahmed Raza", "Administration", 11, "Principal"),
    (8, "Hina Javed", "Academics", 14, "Principal"),
    (9, "Zain Ali", "Finance", 10, "Principal"),
    (10, "Maham Khan", "IT Department", 13, "Principal"),
    (11, "Danish Iqbal", "Hostel", 8, "Principal"),
    (12, "Sadia Aslam", "Library", 12, "Principal"),
    (13, "Noman Saeed", "Transport", 7, "Principal"),
    (14, "Iqra Shah", "Examination", 10, "Principal"),
    (15, "Hamza Tariq", "Security", 9, "Principal"),
    (16, "Maira Anwar", "Admissions", 11, "Principal"),
    (17, "Fahad Sheikh", "Procurement", 8, "Principal"),
    (18, "Komal Batool", "Student Affairs", 12, "Principal"),
    (19, "Rizwan Akhtar", "Maintenance", 10, "Principal"),
    (20, "Nida Rehman", "Academics", 14, "Principal"),
    (21, "Taha Hussain", "Administration", 9, "Principal"),
    (22, "Sana Ilyas", "Finance", 11, "Principal"),
    (23, "Omar Farooq", "IT Department", 13, "Principal"),
    (24, "Laiba Qureshi", "Human Resource", 12, "Principal"),
    (25, "Waqas Mehmood", "Hostel", 10, "Principal")
]

for emp in employees:
    add_employee(*emp)

# Login users. No password is written in the code: set it in .env (SEED_PASSWORD_HR, ...) or a random one is
# generated and printed once at the end. Only the hash is stored in MongoDB (see add_user).
load_dotenv()
users = [
    ("hr@intellihr.com", "SEED_PASSWORD_HR", "hr", "HR Manager", None, None),
    ("supervisor@intellihr.com", "SEED_PASSWORD_SUPERVISOR", "supervisor", "Principal", None, "Principal"),
    ("aliahmad@intellihr.com", "SEED_PASSWORD_ALI", "employee", "Ali Ahmad", 1, "Principal"),
    ("sara@intellihr.com", "SEED_PASSWORD_SARA", "employee", "Sara Khan", 2, "Principal"),
]
generated = []
for username, env_name, role, name, employee_id, supervisor_name in users:
    password = os.getenv(env_name, "").strip()
    if not password:
        password = secrets.token_urlsafe(9)
        generated.append((username, password))
    add_user(username, password, role, name, employee_id, supervisor_name)

print("MongoDB seeded successfully.")
print("25 employees added.")
print("Login users added (passwords stored as hashes).")
if generated:
    print("Generated passwords, shown only now. Save them or set SEED_PASSWORD_* in .env and seed again:")
    for username, password in generated:
        print(f"  {username}  {password}")