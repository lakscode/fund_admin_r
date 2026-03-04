from flask import Blueprint, request, jsonify
import bcrypt
import jwt
import datetime

from config import JWT_SECRET_KEY, JWT_ACCESS_TOKEN_EXPIRES_HOURS
from db import db

auth_bp = Blueprint("auth", __name__, url_prefix="/api")

users_collection = db["users"]


def generate_token(user_id, email):
    payload = {
        "user_id": str(user_id),
        "email": email,
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=JWT_ACCESS_TOKEN_EXPIRES_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    name = data.get("name", "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 409

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    user = {
        "email": email,
        "password": hashed_password,
        "name": name or email.split("@")[0],
        "role": "Portfolio Manager",
        "created_at": datetime.datetime.now(datetime.timezone.utc),
    }

    result = users_collection.insert_one(user)
    token = generate_token(result.inserted_id, email)

    return jsonify({
        "message": "User registered successfully",
        "token": token,
        "user": {
            "id": str(result.inserted_id),
            "email": email,
            "name": user["name"],
            "role": user["role"],
        },
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
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user["name"],
            "role": user.get("role", ""),
        },
    }), 200
