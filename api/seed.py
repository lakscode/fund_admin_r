"""Seed the database with sample roles and users. Run: python seed.py"""

import bcrypt
import datetime
from db import db

roles_collection = db["roles"]
users_collection = db["users"]

SAMPLE_ROLES = [
    {
        "name": "Administrator",
        "description": "Full system access with all permissions",
        "permissions": ["read", "write", "delete", "manage_users", "manage_roles", "manage_settings"],
    },
    {
        "name": "Portfolio Manager",
        "description": "Manage fund portfolios and assets",
        "permissions": ["read", "write", "manage_assets", "manage_funds"],
    },
    {
        "name": "Fund Accountant",
        "description": "Handle fund accounting and financial reporting",
        "permissions": ["read", "write", "manage_accounting", "manage_reports"],
    },
    {
        "name": "Asset Manager",
        "description": "Manage individual property assets and leasing",
        "permissions": ["read", "write", "manage_assets", "manage_leasing"],
    },
    {
        "name": "Compliance Officer",
        "description": "Monitor regulatory compliance and auditing",
        "permissions": ["read", "manage_compliance", "manage_reports"],
    },
]

SAMPLE_USERS = [
    {
        "email": "alex.ferguson@contractio.com",
        "password": "password123",
        "name": "Alex Ferguson",
        "role": "Portfolio Manager",
    },
    {
        "email": "sarah.chen@contractio.com",
        "password": "password123",
        "name": "Sarah Chen",
        "role": "Fund Accountant",
    },
    {
        "email": "james.wilson@contractio.com",
        "password": "password123",
        "name": "James Wilson",
        "role": "Asset Manager",
    },
    {
        "email": "maria.lopez@contractio.com",
        "password": "password123",
        "name": "Maria Lopez",
        "role": "Compliance Officer",
    },
    {
        "email": "admin@contractio.com",
        "password": "admin123",
        "name": "Admin User",
        "role": "Administrator",
    },
]


def seed_roles():
    roles_collection.create_index("name", unique=True)
    inserted = 0
    skipped = 0

    for role_data in SAMPLE_ROLES:
        if roles_collection.find_one({"name": role_data["name"]}):
            print(f"  Skipped (exists): {role_data['name']}")
            skipped += 1
            continue

        roles_collection.insert_one(role_data)
        print(f"  Inserted: {role_data['name']}")
        inserted += 1

    print(f"  Roles done: {inserted} inserted, {skipped} skipped\n")


def seed_users():
    users_collection.create_index("email", unique=True)
    inserted = 0
    skipped = 0

    for user_data in SAMPLE_USERS:
        if users_collection.find_one({"email": user_data["email"]}):
            print(f"  Skipped (exists): {user_data['email']}")
            skipped += 1
            continue

        role = roles_collection.find_one({"name": user_data["role"]})
        role_id = role["_id"] if role else None

        hashed = bcrypt.hashpw(user_data["password"].encode("utf-8"), bcrypt.gensalt())
        doc = {
            "email": user_data["email"],
            "password": hashed,
            "name": user_data["name"],
            "role_id": str(role_id),
            "created_at": datetime.datetime.now(datetime.timezone.utc),
        }
        users_collection.insert_one(doc)
        print(f"  Inserted: {user_data['email']} -> {user_data['role']}")
        inserted += 1

    print(f"  Users done: {inserted} inserted, {skipped} skipped")


if __name__ == "__main__":
    print("Seeding roles...\n")
    seed_roles()
    print("Seeding users...\n")
    seed_users()
