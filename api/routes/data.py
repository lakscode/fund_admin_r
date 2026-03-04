from flask import Blueprint, request, jsonify

from db import db
from csv_loader import CSV_CONFIG, import_csv, import_all

data_bp = Blueprint("data", __name__, url_prefix="/api/data")


@data_bp.route("/import", methods=["POST"])
def import_data():
    """Import CSV files into MongoDB. Optionally pass {"file": "filename.csv"} to import one."""
    body = request.get_json(silent=True)
    filename = body.get("file") if body else None

    if filename:
        if filename not in CSV_CONFIG:
            available = list(CSV_CONFIG.keys())
            return jsonify({"error": f"Unknown file: {filename}", "available": available}), 400
        result = import_csv(filename)
        return jsonify({"message": "Import complete", "result": result}), 200

    results = import_all()
    return jsonify({"message": "All imports complete", "results": results}), 200


@data_bp.route("/totals", methods=["GET"])
def get_totals():
    """Get trial balance / totals data. Optional ?level=2 to filter summary rows."""
    level = request.args.get("level", type=int)
    query = {"level": level} if level is not None else {}

    docs = []
    for doc in db["totals_data"].find(query, {"_id": 0}):
        docs.append(doc)
    return jsonify({"count": len(docs), "data": docs}), 200


@data_bp.route("/properties", methods=["GET"])
def get_properties():
    """Get property data. Optional ?city=Edmonton to filter."""
    query = {}
    city = request.args.get("city")
    province = request.args.get("province")
    if city:
        query["city"] = {"$regex": city, "$options": "i"}
    if province:
        query["province"] = province.upper()

    docs = []
    for doc in db["properties"].find(query, {"_id": 0, "_extra": 0}):
        docs.append(doc)
    return jsonify({"count": len(docs), "data": docs}), 200


@data_bp.route("/fund-tree", methods=["GET"])
def get_fund_tree():
    """Get fund hierarchy tree. Optional ?h_fund=563 to filter."""
    query = {}
    h_fund = request.args.get("h_fund", type=int)
    h_investor = request.args.get("h_investor", type=int)
    if h_fund:
        query["h_fund"] = h_fund
    if h_investor:
        query["h_investor"] = h_investor

    docs = []
    for doc in db["fund_tree"].find(query, {"_id": 0}):
        docs.append(doc)
    return jsonify({"count": len(docs), "data": docs}), 200


@data_bp.route("/collections", methods=["GET"])
def list_collections():
    """List all data collections and their document counts."""
    collections = {}
    for config in CSV_CONFIG.values():
        name = config["collection"]
        collections[name] = db[name].count_documents({})
    return jsonify({"collections": collections}), 200
