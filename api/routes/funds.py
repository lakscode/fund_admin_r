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


def get_fund_overview():
    """Compute fund-level KPIs from GL data."""
    nav = abs(safe_get("29999999"))
    total_equity = abs(safe_get("35009999"))
    total_assets = abs(safe_get("19999999"))
    total_liabilities = abs(safe_get("29999998"))
    net_income = abs(safe_get("99009999"))
    noi = abs(safe_get("79999999"))
    cash = abs(safe_get("10009999"))
    debt = abs(safe_get("23009999"))

    ltv = (debt / total_assets * 100) if total_assets else 0
    ytd_return = (net_income / total_equity * 100) if total_equity else 0

    return {
        "nav": fmt_currency(nav),
        "totalEquity": fmt_currency(total_equity),
        "totalAssets": fmt_currency(total_assets),
        "totalLiabilities": fmt_currency(total_liabilities),
        "netIncome": fmt_currency(net_income),
        "noi": fmt_currency(noi),
        "cash": fmt_currency(cash),
        "totalDebt": fmt_currency(debt),
        "ltv": fmt_pct(ltv),
        "ytdReturn": fmt_pct(ytd_return),
    }


def get_fund_structure():
    """Build fund hierarchy from fund_tree collection."""
    tree_docs = list(fund_tree.find({}, {"_id": 0}))

    # Get unique investors under the root fund
    root_fund = None
    investors = {}
    for doc in tree_docs:
        h_fund = doc.get("h_fund")
        h_investor = doc.get("h_investor")
        h_investment = doc.get("h_investment")
        if root_fund is None:
            root_fund = h_fund

        if h_investor and h_investor != h_fund:
            if h_investor not in investors:
                investors[h_investor] = set()
            if h_investment and h_investment != h_investor:
                investors[h_investor].add(h_investment)

    structure = []
    for inv_id, investments in investors.items():
        structure.append({
            "entityId": inv_id,
            "entityName": f"Entity {inv_id}",
            "investmentCount": len(investments),
        })

    # Sort by investment count descending, take top entries
    structure.sort(key=lambda x: x["investmentCount"], reverse=True)
    return structure[:15]


def get_property_allocation():
    """Aggregate property values by city for allocation breakdown."""
    pipeline = [
        {"$match": {"property_name": {"$ne": None}, "market_value": {"$gt": 0}}},
        {"$group": {
            "_id": "$city",
            "totalValue": {"$sum": "$market_value"},
            "count": {"$sum": 1},
        }},
        {"$sort": {"totalValue": -1}},
    ]
    results = list(properties.aggregate(pipeline))

    total_mv = sum(r["totalValue"] for r in results)
    allocations = []
    for r in results:
        pct = (r["totalValue"] / total_mv * 100) if total_mv else 0
        allocations.append({
            "city": r["_id"] or "Unknown",
            "value": fmt_currency(r["totalValue"]),
            "percentage": round(pct, 1),
            "propertyCount": r["count"],
        })
    return allocations


def get_investor_list():
    """Return investors from funds collection or derive from fund_tree."""
    investors = list(funds_col.find(
        {"type": "investor"},
        {"_id": 0},
    ).sort("committed", -1).limit(10))

    if investors:
        return investors

    # Derive from fund_tree: unique direct investors under root
    tree_docs = list(fund_tree.find({}, {"_id": 0}))
    root_fund = tree_docs[0]["h_fund"] if tree_docs else None
    direct = set()
    for doc in tree_docs:
        if doc.get("h_fund") == root_fund and doc.get("h_investor") == root_fund:
            direct.add(doc.get("h_investment"))

    return [
        {
            "name": f"Investment Vehicle {vid}",
            "entityId": vid,
            "type": "LP",
        }
        for vid in sorted(direct)
    ]


@funds_bp.route("/funds", methods=["GET"])
def funds():
    """Full funds dashboard payload."""
    has_data = totals.count_documents({}) > 0
    prop_count = properties.count_documents({"property_name": {"$ne": None}})

    overview = get_fund_overview() if has_data else {}

    data = {
        "page": {
            "title": "Fund Overview",
            "subtitle": "Horizon Value Fund I · Fund structure, NAV and investor summary",
        },
        "tabs": ["Overview", "Investors", "Structure", "Distributions", "Documents"],
        "overview": overview,
        "stats": {
            "propertyCount": prop_count,
            "investorCount": len(get_investor_list()),
            "fundTreeEntities": fund_tree.count_documents({}),
        },
        "allocation": get_property_allocation(),
        "investors": get_investor_list(),
        "structure": get_fund_structure(),
    }
    return jsonify(data), 200
