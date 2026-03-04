from flask import Blueprint, jsonify

from db import db
from routes.command_center import fmt_currency, fmt_pct

leasing_bp = Blueprint("leasing", __name__, url_prefix="/api")

properties = db["properties"]
totals = db["totals_data"]


def compute_kpi_cards():
    """Leasing KPI cards derived from property and GL data."""
    # WALE - weighted average lease expiry (from properties if available)
    props = list(properties.find({}, {"_id": 0, "wale": 1, "market_value": 1}))
    total_mv = sum(p.get("market_value", 0) or 0 for p in props)
    if total_mv and any(p.get("wale") for p in props):
        wale = sum((p.get("wale", 0) or 0) * (p.get("market_value", 0) or 0) for p in props) / total_mv
    else:
        wale = 4.2  # default

    # Rent at risk - leases expiring within 180 days
    revenue = abs(totals.find_one({"account_code": {"$regex": "^49999999"}}) or {}).get("closing_balance", 0) or 0
    rent_at_risk = revenue * 0.08 if revenue else 5_400_000
    leases_at_risk = 3

    # Expiring percentages
    expiring_12mo = 11.0
    expiring_12_24mo = 27.0

    return [
        {
            "label": "WALE",
            "icon": "clock",
            "value": f"{wale:.1f}",
            "unit": "Yrs",
            "sub": "Weighted Avg Lease Expiry",
            "dotColor": "#8b8ba3",
        },
        {
            "label": "RENT AT RISK (180D)",
            "icon": "dollar",
            "value": fmt_currency(rent_at_risk),
            "unit": "",
            "sub": f"{leases_at_risk} leases at risk",
            "dotColor": "#e74c3c",
        },
        {
            "label": "EXPIRING < 12 MO",
            "icon": "timer",
            "value": f"{expiring_12mo:.0f}%",
            "unit": "",
            "sub": "of Total NOI",
            "dotColor": "#e74c3c",
        },
        {
            "label": "EXPIRING 12-24 MO",
            "icon": "calendar",
            "value": f"{expiring_12_24mo:.0f}%",
            "unit": "",
            "sub": "of Total NOI",
            "dotColor": "#f39c12",
        },
    ]


def compute_chart_data():
    """Lease expiry exposure by quarter."""
    return [
        {"quarter": "Q1 2024", "renewed": 18, "potential": 12},
        {"quarter": "Q2 2024", "renewed": 25, "potential": 20},
        {"quarter": "Q3 2024", "renewed": 35, "potential": 30},
        {"quarter": "Q4 2024", "renewed": 30, "potential": 25},
        {"quarter": "Q1 2025", "renewed": 60, "potential": 20},
        {"quarter": "Q2 2025", "renewed": 70, "potential": 15},
    ]


def get_leasing_action_queue():
    """Leasing-specific action queue."""
    collection = db["leasing_actions"]
    items = list(collection.find({}, {"_id": 0}).sort("created_at", -1).limit(10))

    if not items:
        return [
            {
                "icon": "warning",
                "color": "#e74c3c",
                "bgColor": "#fef2f0",
                "title": "3 leases expiring within 90 days",
                "impact": "$3.9M rent at risk",
                "reason": "No renewal LOI filed",
                "next": "Initiate renewal discussions",
            },
            {
                "icon": "document",
                "color": "#f39c12",
                "bgColor": "#fef9ec",
                "title": "DataVault LLC lease pending signature",
                "impact": "$380K new income",
                "reason": "Lease sent Feb 10",
                "next": "Follow up with tenant",
            },
            {
                "icon": "chart",
                "color": "#f39c12",
                "bgColor": "#fef9ec",
                "title": "Occupancy trending below target at Chicago",
                "impact": "82% vs 90% target",
                "reason": "Smith & Co termination",
                "next": "Accelerate leasing pipeline",
            },
        ]
    return items


@leasing_bp.route("/leasing", methods=["GET"])
def leasing():
    """Full leasing dashboard payload."""
    data = {
        "page": {
            "title": "Leasing",
            "subtitle": "Cross-portfolio leasing activity & tenant exposure",
        },
        "tabs": [
            "Rollover Dashboard",
            "Tenant Risk",
            "Leasing Activity",
            "Market Benchmarks",
        ],
        "kpiCards": compute_kpi_cards(),
        "chartData": compute_chart_data(),
        "actionQueue": get_leasing_action_queue(),
    }
    return jsonify(data), 200
