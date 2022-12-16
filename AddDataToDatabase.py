
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
print("DB URL", DATABASE_URL)
cred = credentials.Certificate("service-account-key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': DATABASE_URL
})

ref = db.reference('Students')

# 00:54:34 is the time
data = {
    '246324':
    {
        "name": "Elon Musk",
        "major": "Physics",
        "starting_year": 1994,
        "total_attendance": 1,
        "standing": "G",
        "year": 5,
        "last_attendance_time": "2022-12-15 00:54:34"
    },
    '663532':
    {
        "name": "Holland Pleskac",
        "major": "Computer Science",
        "starting_year": 2022,
        "total_attendance": 1,
        "standing": "G",
        "year": 1,
        "last_attendance_time": "2022-12-15 00:44:34"
    },
    '928384':
    {
        "name": "Emily Blunt",
        "major": "Acting",
        "starting_year": 2005,
        "total_attendance": 1,
        "standing": "G",
        "year": 4,
        "last_attendance_time": "2022-12-15 03:14:34"
    }
}

for key, value in data.items():
    ref.child(key).set(value)
    
    print("added key:", key, "\nvalue:", value)


