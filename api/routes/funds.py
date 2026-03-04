from flask import Blueprint, jsonify

from db import db
from routes.command_center import fmt_currency, fmt_pct

funds_bp = Blueprint("funds", __name__, url_prefix="/api")

totals = db["totals_data"]
properties = db["properties"]
fund_tree = db["fund_tree"]
funds_col = db["funds"]


def safe_get(account_code, field="closing_balance"):
    doc = totals.find_one({"account_code": {"$regex": f"^{account_code}"}})
    if doc:
        return doc.get(field, 0.0) or 0.0
    return 0.0


@funds_bp.route("/funds", methods=["GET"])
def funds():
    """Funds list table payload."""
    has_data = totals.count_documents({}) > 0
    prop_count = properties.count_documents({"property_name": {"$ne": None}})

    if has_data:
        total_assets = abs(safe_get("19999999"))
        total_equity = abs(safe_get("35009999"))
        cash = abs(safe_get("10009999"))
        net_income = abs(safe_get("99009999"))
        ytd_return = (net_income / total_equity * 100) if total_equity else 0

        fund_row = {
            "name": "Horizon Value Fund I",
            "aum": fmt_currency(total_assets),
            "eum": fmt_currency(total_equity),
            "cash": fmt_currency(cash),
            "properties": prop_count,
            "ytdReturn": fmt_pct(ytd_return),
            "status": "Active",
        }
    else:
        fund_row = {
            "name": "Horizon Value Fund I",
            "aum": "$1.2B",
            "eum": "$552M",
            "cash": "$11.3M",
            "properties": 3,
            "ytdReturn": "8.2%",
            "status": "Active",
        }

    data = {
        "page": {
            "title": "Funds",
            "subtitle": "Fund-level capital, NAV, and reporting",
        },
        "funds": [fund_row],
    }
    return jsonify(data), 200
