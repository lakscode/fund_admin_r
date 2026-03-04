from flask import Blueprint, jsonify

from db import client

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.route("/health", methods=["GET"])
def health():
    try:
        client.admin.command("ping")
        return jsonify({"status": "ok", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "error", "database": str(e)}), 500
