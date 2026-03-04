from flask import Blueprint, jsonify, request

from db import db
from routes.command_center import fmt_currency, fmt_pct

assets_bp = Blueprint("assets", __name__, url_prefix="/api")

properties = db["properties"]
totals = db["totals_data"]


def build_property_list():
    """Build asset performance rows from properties collection."""
    props = list(properties.find(
        {"property_name": {"$ne": None}},
        {"_id": 0},
    ))

    results = []
    for i, p in enumerate(props):
        mv = p.get("market_value", 0) or 0
        noi = p.get("noi", 0) or 0
        budget = p.get("budget_noi", 0) or 0
        occupancy = p.get("occupancy", 0) or 0
        dscr = p.get("dscr", 0) or 0

        # NOI vs Budget
        if budget:
            noi_vs = ((noi - budget) / abs(budget)) * 100
            noi_vs_str = f"{'+' if noi_vs >= 0 else ''}{noi_vs:.1f}%"
            noi_vs_type = "positive" if noi_vs >= 0 else "negative"
        else:
            noi_vs_str = "N/A"
            noi_vs_type = "neutral"

        # Risk scoring
        if dscr and dscr < 1.25:
            risk = "High"
        elif occupancy and occupancy < 90:
            risk = "High" if occupancy < 85 else "Medium"
        elif noi_vs_type == "negative":
            risk = "Medium"
        else:
            risk = "Low"

        # Month-end status
        month_end_val = p.get("month_end_status", "NOT STARTED")

        results.append({
            "name": p.get("property_name", "Unknown"),
            "id": p.get("property_id", f"#P-{i+1:04d}"),
            "market": p.get("city", ""),
            "type": p.get("property_type", "Mixed-Use"),
            "noiYtd": fmt_currency(noi) if noi else "$0",
            "noiVsBudget": noi_vs_str,
            "noiVsType": noi_vs_type,
            "occupancy": f"{occupancy:.0f}%" if occupancy else "N/A",
            "dscr": f"{dscr:.2f}x" if dscr else "N/A",
            "rentExpiring": fmt_currency(p.get("rent_expiring", 0) or 0),
            "risk": risk,
            "monthEnd": month_end_val,
        })

    return results


def compute_summary_cards(props):
    """Compute summary cards from property data."""
    # Aggregate DSCR
    noi = abs((totals.find_one({"account_code": {"$regex": "^79999999"}}) or {}).get("closing_balance", 0) or 0)
    debt_service = abs((totals.find_one({"account_code": {"$regex": "^80004999"}}) or {}).get("closing_balance", 0) or 0)
    dscr = (noi / debt_service) if debt_service else 1.52

    # Avg Occupancy
    occ_values = [p.get("occupancy", 0) or 0 for p in props if p.get("occupancy")]
    avg_occ = sum(occ_values) / len(occ_values) if occ_values else 90.2

    # Expiring revenue
    total_expiring = sum(p.get("rent_expiring", 0) or 0 for p in props)
    if not total_expiring:
        total_expiring = 10_400_000

    health = "High" if avg_occ >= 90 else ("Medium" if avg_occ >= 80 else "Low")

    return [
        {
            "label": "AGGREGATE DSCR",
            "icon": "trend",
            "value": f"{dscr:.2f}x",
            "sub": f"{'Above' if dscr >= 1.25 else 'Below'} 1.25x covenant",
            "subColor": "#27ae60" if dscr >= 1.25 else "#e74c3c",
            "accent": "#e8a838",
        },
        {
            "label": "AVG. OCCUPANCY",
            "icon": "clock",
            "value": f"{avg_occ:.1f}%",
            "sub": f"Portfolio health: {health}",
            "subColor": "#8b8ba3",
            "accent": "#27ae60",
        },
        {
            "label": "EXPIRING REVENUE",
            "icon": "calendar",
            "value": fmt_currency(total_expiring),
            "sub": "Due within next 180 days",
            "subColor": "#8b8ba3",
            "accent": "#8b8ba3",
        },
    ]


def get_filters(props):
    """Extract unique filter values from properties."""
    markets = sorted(set(p.get("city", "") for p in props if p.get("city")))
    types = sorted(set(p.get("property_type", "") for p in props if p.get("property_type")))
    return {
        "markets": ["All Markets"] + markets,
        "types": ["All Types"] + types,
    }


@assets_bp.route("/assets", methods=["GET"])
def assets():
    """Full assets dashboard payload."""
    prop_docs = list(properties.find({"property_name": {"$ne": None}}, {"_id": 0}))
    prop_list = build_property_list()

    # Use DB-derived filters or defaults
    filters = get_filters(prop_docs)
    if len(filters["markets"]) <= 1:
        filters = {
            "markets": ["All Markets", "Chicago", "Dallas", "Phoenix", "Austin"],
            "types": ["All Types", "Mixed-Use", "Industrial", "Office"],
        }

    data = {
        "page": {
            "title": "Asset Performance",
            "subtitle": "Real-time property list ranked by risk and operational performance.",
        },
        "properties": prop_list if prop_list else None,
        "pagination": {
            "totalItems": len(prop_list) if prop_list else 24,
            "itemsPerPage": 10,
        },
        "filters": filters,
        "summaryCards": compute_summary_cards(prop_docs),
    }
    return jsonify(data), 200
