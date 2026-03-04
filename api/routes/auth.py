from flask import Blueprint, request, jsonify
from bson import ObjectId
import bcrypt
import jwt
import datetime

from config import JWT_SECRET_KEY, JWT_ACCESS_TOKEN_EXPIRES_HOURS
from db import db

auth_bp = Blueprint("auth", __name__, url_prefix="/api")

users_collection = db["users"]
roles_collection = db["roles"]


def generate_token(user_id, email):
    payload = {
        "user_id": str(user_id),
        "email": email,
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=JWT_ACCESS_TOKEN_EXPIRES_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")


def get_role_name(role_id):
    if not role_id:
        return ""
    role = roles_collection.find_one({"_id": role_id})
    return role["name"] if role else ""


def build_user_response(user):
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "name": user["name"],
        "role_id": str(user.get("role_id", "")),
        "role": get_role_name(user.get("role_id")),
    }


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    name = data.get("name", "").strip()
    role_id = data.get("role_id", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 409

    # Validate and resolve role
    resolved_role_id = None
    if role_id:
        if not ObjectId.is_valid(role_id):
            return jsonify({"error": "Invalid role_id"}), 400
        role = roles_collection.find_one({"_id": ObjectId(role_id)})
        if not role:
            return jsonify({"error": "Role not found"}), 404
        resolved_role_id = role["_id"]
    else:
        # Default to "Portfolio Manager" role
        default_role = roles_collection.find_one({"name": "Portfolio Manager"})
        if default_role:
            resolved_role_id = default_role["_id"]

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    user = {
        "email": email,
        "password": hashed_password,
        "name": name or email.split("@")[0],
        "role_id": resolved_role_id,
        "created_at": datetime.datetime.now(datetime.timezone.utc),
    }

    result = users_collection.insert_one(user)
    user["_id"] = result.inserted_id
    token = generate_token(result.inserted_id, email)

    return jsonify({
        "message": "User registered successfully",
        "token": token,
        "user": build_user_response(user),
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    if not bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    token = generate_token(user["_id"], email)

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": build_user_response(user),
    }), 200
