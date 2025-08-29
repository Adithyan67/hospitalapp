import sqlite3

DB = "clinic.db"

doctors = [
    ("Dr. Ravi", "Cardiology"),
    ("Dr. Rahul", "Neurology"),
    ("Dr. Gokul", "Orthopedics"),
]

patients = [
    ("Krishna", "1234567890"),
    ("Kiran", "9876543210"),
    ("Dev", "5556667777"),
]

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.executemany("INSERT INTO doctors (name, department) VALUES (?, ?)", doctors)
cur.executemany("INSERT INTO patients (name, phone) VALUES (?, ?)", patients)

conn.commit()
conn.close()
print("✅ Seed data inserted")
