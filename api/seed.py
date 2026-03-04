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


def seed_dashboard_config():
    collection = db["dashboard_config"]
    config = {
        "page_key": "command_center",
        "page": {
            "title": "Command Center",
            "subtitle": "Executive portfolio-wide visibility · Horizon Value Fund I",
        },
        "tabs": [
            "Daily Brief",
            "Performance Summary",
            "Liquidity & Cash",
            "Risk & Valuation",
            "Month-End Control",
            "Data Health",
        ],
        "account_map": {
            "total_assets": "19999999",
            "total_cash": "10009999",
            "total_income": "49999999",
            "noi": "79999999",
            "fund_expenses": "83009999",
            "total_equity": "35009999",
            "debt_service": "80004999",
            "net_income": "99009999",
        },
        "thresholds": {
            "expense_ratio_warn": 35,
            "dscr_covenant": 1.25,
            "at_risk_market_value": 3000000,
            "occupancy_target": 90,
        },
    }

    collection.delete_many({"page_key": "command_center"})
    collection.insert_one(config)
    print("  Inserted: command_center dashboard config")


def seed_action_queue():
    collection = db["action_queue"]
    collection.drop()
    items = [
        {
            "status": "OVERDUE",
            "statusColor": "#e74c3c",
            "time": "2h ago",
            "title": "Reconcile Q3 Variance - Summit Retail",
            "hasLink": True,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
        },
        {
            "status": "PENDING APPROVAL",
            "statusColor": "#f39c12",
            "time": "Yesterday",
            "title": "Capital Call Notice #42 Distribution",
            "hasLink": False,
            "created_at": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1),
        },
        {
            "status": "IN REVIEW",
            "statusColor": "#3498db",
            "time": "2 days ago",
            "title": "ESB Building 1 - Lease Renewal Approval",
            "hasLink": True,
            "created_at": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=2),
        },
        {
            "status": "PENDING",
            "statusColor": "#8b8ba3",
            "time": "3 days ago",
            "title": "Monthly NAV Calculation - Fund I",
            "hasLink": True,
            "created_at": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=3),
        },
    ]
    collection.insert_many(items)
    print(f"  Inserted: {len(items)} action queue items")


def seed_return_history():
    collection = db["return_history"]
    collection.drop()
    records = [
        {"period": "1Y", "fund_return": 97.5, "benchmark_return": 61.4},
        {"period": "3Y", "fund_return": 80.0, "benchmark_return": 50.7},
        {"period": "5Y", "fund_return": 92.6, "benchmark_return": 56.6},
    ]
    collection.insert_many(records)
    print(f"  Inserted: {len(records)} return history records")


if __name__ == "__main__":
    print("Seeding roles...\n")
    seed_roles()
    print("Seeding users...\n")
    seed_users()
    print("\nSeeding dashboard config...\n")
    seed_dashboard_config()
    print("\nSeeding action queue...\n")
    seed_action_queue()
    print("\nSeeding return history...\n")
    seed_return_history()
