from mongo_database import employees_collection,leave_requests_collection, users_collection, add_employee

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

# Login users
users_collection.insert_many([
    {
        "username": "hr@intellihr.com",
        "password": "Hr@2026",
        "role": "hr",
        "name": "HR Manager"
    },
    {
        "username": "supervisor@intellihr.com",
        "password": "Sup@2026",
        "role": "supervisor",
        "name": "Principal",
        "supervisor_name": "Principal"
    },
    {
        "username": "aliahmad@intellihr.com",
        "password": "Ali@2026",
        "role": "employee",
        "name": "Ali Ahmad",
        "employee_id": 1,
        "supervisor_name": "Principal"
    },
    {
        "username": "sara@intellihr.com",
        "password": "Sara@2026",
        "role": "employee",
        "name": "Sara Khan",
        "employee_id": 2,
        "supervisor_name": "Principal"
    }
])

print("MongoDB seeded successfully.")
print("25 employees added.")
print("Login users added.")