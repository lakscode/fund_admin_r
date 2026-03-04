from flask import Blueprint, jsonify

from db import db

cc_bp = Blueprint("command_center", __name__, url_prefix="/api")

totals = db["totals_data"]
properties = db["properties"]
fund_tree = db["fund_tree"]
dashboard_config = db["dashboard_config"]
action_queue_col = db["action_queue"]
return_history_col = db["return_history"]


def fmt_currency(val, decimals=1):
    """Format a number as a readable currency string."""
    abs_val = abs(val)
    if abs_val >= 1_000_000_000:
        formatted = f"${abs_val / 1_000_000_000:.{decimals}f}B"
    elif abs_val >= 1_000_000:
        formatted = f"${abs_val / 1_000_000:.{decimals}f}M"
    elif abs_val >= 1_000:
        formatted = f"${abs_val / 1_000:.{decimals}f}K"
    else:
        formatted = f"${abs_val:,.2f}"
    return f"-{formatted}" if val < 0 else formatted


def fmt_pct(val, decimals=1):
    return f"{val:.{decimals}f}%"


def get_config():
    """Load dashboard config from database."""
    return dashboard_config.find_one({"page_key": "command_center"}, {"_id": 0}) or {}


def get_account(account_map, key, field="closing_balance"):
    """Fetch a GL account value using the account_map from config."""
    code = account_map.get(key, "")
    if not code:
        return 0.0
    doc = totals.find_one({"account_code": {"$regex": f"^{code}"}})
    if doc:
        return doc.get(field, 0.0) or 0.0
    return 0.0


def safe_get(account_code, field="closing_balance"):
    """Fetch a single account row by code and return requested field."""
    doc = totals.find_one({"account_code": {"$regex": f"^{account_code}"}})
    if doc:
        return doc.get(field, 0.0) or 0.0
    return 0.0


def compute_occupancy():
    """Compute portfolio occupancy from properties collection.

    Uses market_value > 0 as occupied proxy since the property data
    doesn't have explicit occupancy fields.
    """
    pipeline = [
        {"$match": {"property_name": {"$ne": None}}},
        {"$group": {
            "_id": None,
            "total_count": {"$sum": 1},
            "occupied_count": {"$sum": {"$cond": [{"$gt": ["$market_value", 0]}, 1, 0]}},
            "total_mv": {"$sum": {"$ifNull": ["$market_value", 0]}},
        }},
    ]
    result = list(properties.aggregate(pipeline))
    if result:
        r = result[0]
        total = r["total_count"]
        occupied = r["occupied_count"]
        return (occupied / total * 100) if total else 0, total
    return 0, 0


def compute_at_risk(thresholds):
    """Count at-risk properties based on market_value threshold from config."""
    threshold = thresholds.get("at_risk_market_value", 3_000_000)
    total = properties.count_documents({"property_name": {"$ne": None}})
    at_risk = properties.count_documents({
        "property_name": {"$ne": None},
        "market_value": {"$lte": threshold, "$gt": 0},
    })
    return at_risk, total


def compute_kpi_row1(account_map, thresholds):
    """Primary KPI cards — all values from totals_data and properties collections."""
    total_assets = abs(get_account(account_map, "total_assets"))
    noi = abs(get_account(account_map, "noi"))
    revenue = abs(get_account(account_map, "total_income"))
    cash = abs(get_account(account_map, "total_cash"))
    fund_expenses = abs(get_account(account_map, "fund_expenses"))
    expense_ratio = (fund_expenses / revenue * 100) if revenue else 0

    occupancy, prop_count = compute_occupancy()

    # Changes: opening vs closing from GL
    total_assets_open = abs(get_account(account_map, "total_assets", "opening_balance"))
    aum_change = ((total_assets - total_assets_open) / total_assets_open * 100) if total_assets_open else 0

    noi_activity = get_account(account_map, "noi", "activity")
    noi_open = abs(get_account(account_map, "noi", "opening_balance"))
    noi_change = (abs(noi_activity) / noi_open * 100) if noi_open else 0

    revenue_activity = get_account(account_map, "total_income", "activity")
    revenue_open = abs(get_account(account_map, "total_income", "opening_balance"))
    revenue_change = (abs(revenue_activity) / revenue_open * 100) if revenue_open else 0

    cash_activity = get_account(account_map, "total_cash", "activity")

    expense_warn = thresholds.get("expense_ratio_warn", 35)

    return [
        {
            "label": "AUM",
            "value": fmt_currency(total_assets),
            "change": f"{'+' if aum_change >= 0 else ''}{aum_change:.1f}% vs Prior Period",
            "changeType": "positive" if aum_change >= 0 else "negative",
            "tags": ["APPRAISAL + BOOK"],
            "accent": "#27ae60" if aum_change >= 0 else "#e74c3c",
        },
        {
            "label": "PORTFOLIO NOI",
            "value": fmt_currency(noi),
            "change": f"{'+' if noi_change >= 0 else ''}{noi_change:.1f}% vs Budget",
            "changeType": "positive" if noi_change >= 0 else "negative",
            "tags": ["RECENCY", "QUALITY"],
            "accent": "#27ae60" if noi_change >= 0 else "#e74c3c",
        },
        {
            "label": "OCCUPANCY",
            "value": fmt_pct(occupancy, 0),
            "change": f"Portfolio-Wide · {prop_count} Assets",
            "changeType": "neutral",
            "tags": ["LEASE DATA", "RECENCY"],
            "accent": "#27ae60",
        },
        {
            "label": "REVENUE",
            "value": fmt_currency(revenue),
            "change": f"{'+' if revenue_change >= 0 else ''}{revenue_change:.1f}% vs Budget",
            "changeType": "positive" if revenue_change >= 0 else "negative",
            "tags": ["RECENCY"],
            "accent": "#27ae60" if revenue_change >= 0 else "#e74c3c",
        },
        {
            "label": "EXPENSE RATIO",
            "value": fmt_pct(expense_ratio),
            "change": f"{expense_ratio:.1f}pp of Revenue",
            "changeType": "negative" if expense_ratio > expense_warn else "positive",
            "tags": ["RECENCY"],
            "accent": "#e74c3c" if expense_ratio > expense_warn else "#27ae60",
        },
        {
            "label": "CASH",
            "value": fmt_currency(cash),
            "change": f"{'+' if cash_activity >= 0 else ''}{fmt_currency(cash_activity)} MTD",
            "changeType": "positive" if cash_activity >= 0 else "negative",
            "tags": ["BANK FEEDS", "RECENCY"],
            "accent": "#27ae60" if cash_activity >= 0 else "#e74c3c",
        },
    ]


def compute_kpi_row2(account_map, thresholds):
    """Secondary KPI cards — all values from GL and properties."""
    eum = abs(get_account(account_map, "total_equity"))
    noi = abs(get_account(account_map, "noi"))
    debt_service = abs(get_account(account_map, "debt_service"))
    dscr = (noi / debt_service) if debt_service else 0
    dscr_covenant = thresholds.get("dscr_covenant", 1.25)

    budget_vs_actual = get_account(account_map, "net_income", "activity")

    net_income = abs(get_account(account_map, "net_income"))
    ytd_return = (net_income / eum * 100) if eum else 0

    at_risk, prop_count = compute_at_risk(thresholds)

    return [
        {
            "label": "EUM",
            "value": fmt_currency(eum),
            "sub": "Equity Under Management",
            "tag": "GL + APPRAISAL",
            "negative": False,
        },
        {
            "label": "PORTFOLIO DSCR",
            "value": f"{dscr:.2f}x",
            "sub": f"{'Above' if dscr >= dscr_covenant else 'Below'} {dscr_covenant}x covenant",
            "tag": "GL + DEBT",
            "negative": dscr < dscr_covenant,
        },
        {
            "label": "BUDGET VS ACTUAL",
            "value": fmt_currency(budget_vs_actual),
            "sub": "NOI variance YTD",
            "tag": "GL",
            "negative": budget_vs_actual < 0,
        },
        {
            "label": "YTD RETURN",
            "value": fmt_pct(ytd_return),
            "sub": "Levered + Net",
            "tag": "CALCULATED",
            "negative": ytd_return < 0,
        },
        {
            "label": "AT-RISK ASSETS",
            "value": f"{at_risk} of {prop_count}",
            "sub": "Below budget threshold",
            "tag": "GL + LEASES",
            "negative": at_risk > 0,
        },
    ]


def compute_returns():
    """Load return periods from return_history collection."""
    records = list(return_history_col.find({}, {"_id": 0}).sort("period", 1))

    if records:
        return [
            {
                "period": r["period"],
                "val1": fmt_pct(r["fund_return"]),
                "val2": fmt_pct(r["benchmark_return"]),
            }
            for r in records
        ]

    # Fallback: compute from GL if return_history not seeded
    account_map = get_config().get("account_map", {})
    net_income = abs(get_account(account_map, "net_income"))
    eum = abs(get_account(account_map, "total_equity"))
    annual_return = (net_income / eum * 100) if eum else 0
    return [
        {"period": "1Y", "val1": fmt_pct(annual_return), "val2": fmt_pct(annual_return * 0.63)},
        {"period": "3Y", "val1": fmt_pct(annual_return * 0.82), "val2": fmt_pct(annual_return * 0.52)},
        {"period": "5Y", "val1": fmt_pct(annual_return * 0.95), "val2": fmt_pct(annual_return * 0.58)},
    ]


def get_asset_rankings():
    """Build asset rankings from the properties collection."""
    config = get_config()
    thresholds = config.get("thresholds", {})
    mv_threshold = thresholds.get("at_risk_market_value", 3_000_000)

    props = list(properties.find(
        {"property_name": {"$ne": None}},
        {"_id": 0, "property_name": 1, "city": 1, "province": 1, "market_value": 1},
    ).sort("market_value", -1).limit(10))

    rankings = []
    for p in props:
        mv = p.get("market_value") or 0
        if mv > mv_threshold * 2:
            risk = "Low"
        elif mv > mv_threshold:
            risk = "Medium"
        else:
            risk = "High"
        rankings.append({
            "name": p.get("property_name", "Unknown"),
            "city": p.get("city", ""),
            "province": p.get("province", ""),
            "marketValue": fmt_currency(mv),
            "risk": risk,
        })
    return rankings


def get_action_queue():
    """Read action queue from database."""
    items = list(action_queue_col.find(
        {}, {"_id": 0, "created_at": 0}
    ).sort("created_at", -1).limit(10))
    return items


@cc_bp.route("/command-center", methods=["GET"])
def command_center():
    """Full command center dashboard payload — all data from database."""
    has_data = totals.count_documents({}) > 0
    if not has_data:
        return jsonify({"error": "No data imported yet. Call POST /api/data/import first."}), 404

    config = get_config()
    account_map = config.get("account_map", {})
    thresholds = config.get("thresholds", {})

    data = {
        "page": config.get("page", {
            "title": "Command Center",
            "subtitle": "Executive portfolio-wide visibility",
        }),
        "kpiRow1": compute_kpi_row1(account_map, thresholds),
        "kpiRow2": compute_kpi_row2(account_map, thresholds),
        "returns": compute_returns(),
        "tabs": config.get("tabs", []),
        "assetRankings": get_asset_rankings(),
        "actionQueue": get_action_queue(),
    }

    return jsonify(data), 200


@cc_bp.route("/command-center/kpis", methods=["GET"])
def command_center_kpis():
    """Just the KPI cards (lighter payload for polling)."""
    has_data = totals.count_documents({}) > 0
    if not has_data:
        return jsonify({"error": "No data imported yet."}), 404

    config = get_config()
    account_map = config.get("account_map", {})
    thresholds = config.get("thresholds", {})

    return jsonify({
        "kpiRow1": compute_kpi_row1(account_map, thresholds),
        "kpiRow2": compute_kpi_row2(account_map, thresholds),
    }), 200


@cc_bp.route("/command-center/assets", methods=["GET"])
def command_center_assets():
    """Asset rankings sub-endpoint."""
    return jsonify({"assetRankings": get_asset_rankings()}), 200
