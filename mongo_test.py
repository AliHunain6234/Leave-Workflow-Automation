from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["hr_leave_system"]

print("Employees count:", db["employees"].count_documents({}))

for emp in db["employees"].find().sort("employee_id", -1).limit(5):
    print(emp)

print("Connected Successfully")