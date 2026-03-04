from flask import Blueprint, request, jsonify
from bson import ObjectId

from db import db

roles_bp = Blueprint("roles", __name__, url_prefix="/api")

roles_collection = db["roles"]


@roles_bp.route("/roles", methods=["GET"])
def get_roles():
    roles = []
    for role in roles_collection.find():
        roles.append({
            "id": str(role["_id"]),
            "name": role["name"],
            "description": role.get("description", ""),
            "permissions": role.get("permissions", []),
        })
    return jsonify({"roles": roles}), 200


@roles_bp.route("/roles/<role_id>", methods=["GET"])
def get_role(role_id):
    if not ObjectId.is_valid(role_id):
        return jsonify({"error": "Invalid role ID"}), 400

    role = roles_collection.find_one({"_id": ObjectId(role_id)})
    if not role:
        return jsonify({"error": "Role not found"}), 404

    return jsonify({
        "id": str(role["_id"]),
        "name": role["name"],
        "description": role.get("description", ""),
        "permissions": role.get("permissions", []),
    }), 200


@roles_bp.route("/roles", methods=["POST"])
def create_role():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Role name is required"}), 400

    if roles_collection.find_one({"name": name}):
        return jsonify({"error": "Role already exists"}), 409

    role = {
        "name": name,
        "description": data.get("description", ""),
        "permissions": data.get("permissions", []),
    }

    result = roles_collection.insert_one(role)
    return jsonify({
        "message": "Role created successfully",
        "id": str(result.inserted_id),
        "name": name,
        "description": role["description"],
        "permissions": role["permissions"],
    }), 201


@roles_bp.route("/roles/<role_id>", methods=["PUT"])
def update_role(role_id):
    if not ObjectId.is_valid(role_id):
        return jsonify({"error": "Invalid role ID"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    update = {}
    if "name" in data:
        update["name"] = data["name"].strip()
    if "description" in data:
        update["description"] = data["description"]
    if "permissions" in data:
        update["permissions"] = data["permissions"]

    if not update:
        return jsonify({"error": "No fields to update"}), 400

    result = roles_collection.update_one({"_id": ObjectId(role_id)}, {"$set": update})
    if result.matched_count == 0:
        return jsonify({"error": "Role not found"}), 404

    return jsonify({"message": "Role updated successfully"}), 200


@roles_bp.route("/roles/<role_id>", methods=["DELETE"])
def delete_role(role_id):
    if not ObjectId.is_valid(role_id):
        return jsonify({"error": "Invalid role ID"}), 400

    result = roles_collection.delete_one({"_id": ObjectId(role_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Role not found"}), 404

    return jsonify({"message": "Role deleted successfully"}), 200
