"""Seed the database with sample users. Run: python seed.py"""

import bcrypt
import datetime
from db import db

users_collection = db["users"]

SAMPLE_USERS = [
    {
        "email": "alex.ferguson@restackai.com",
        "password": "password123",
        "name": "Alex Ferguson",
        "role": "Portfolio Manager",
    },
    {
        "email": "sarah.chen@restackai.com",
        "password": "password123",
        "name": "Sarah Chen",
        "role": "Fund Accountant",
    },
    {
        "email": "james.wilson@restackai.com",
        "password": "password123",
        "name": "James Wilson",
        "role": "Asset Manager",
    },
    {
        "email": "maria.lopez@restackai.com",
        "password": "password123",
        "name": "Maria Lopez",
        "role": "Compliance Officer",
    },
    {
        "email": "admin@restackai.com",
        "password": "admin123",
        "name": "Admin User",
        "role": "Administrator",
    },
]


def seed():
    users_collection.create_index("email", unique=True)
    inserted = 0
    skipped = 0

    for user_data in SAMPLE_USERS:
        if users_collection.find_one({"email": user_data["email"]}):
            print(f"  Skipped (exists): {user_data['email']}")
            skipped += 1
            continue

        hashed = bcrypt.hashpw(user_data["password"].encode("utf-8"), bcrypt.gensalt())
        doc = {
            "email": user_data["email"],
            "password": hashed,
            "name": user_data["name"],
            "role": user_data["role"],
            "created_at": datetime.datetime.now(datetime.timezone.utc),
        }
        users_collection.insert_one(doc)
        print(f"  Inserted: {user_data['email']}")
        inserted += 1

    print(f"\nDone: {inserted} inserted, {skipped} skipped")


if __name__ == "__main__":
    print("Seeding users...\n")
    seed()
