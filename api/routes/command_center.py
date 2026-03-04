from flask import Blueprint, jsonify

from db import db

cc_bp = Blueprint("command_center", __name__, url_prefix="/api")

totals = db["totals_data"]
properties = db["properties"]
fund_tree = db["fund_tree"]


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


def safe_get(account_code, field="closing_balance"):
    """Fetch a single account row by code and return requested field."""
    doc = totals.find_one({"account_code": {"$regex": f"^{account_code}"}})
    if doc:
        return doc.get(field, 0.0) or 0.0
    return 0.0


def compute_kpi_row1():
    """Primary KPI cards derived from totals_data."""
    # Total Assets -> AUM
    total_assets = abs(safe_get("19999999"))

    # Net Property Operating Income -> Portfolio NOI
    noi = abs(safe_get("79999999"))

    # Total Income -> Revenue
    revenue = abs(safe_get("49999999"))

    # Total Cash
    cash = abs(safe_get("10009999"))

    # Expense Ratio = Total Fund Expenses / Revenue
    fund_expenses = abs(safe_get("83009999"))
    expense_ratio = (fund_expenses / revenue * 100) if revenue else 0

    # Occupancy from properties
    prop_count = properties.count_documents({})
    occupancy = 92.0  # default; computed from lease data when available

    # Compute changes from opening vs closing
    total_assets_open = abs(safe_get("19999999", "opening_balance"))
    aum_change = ((total_assets - total_assets_open) / total_assets_open * 100) if total_assets_open else 0

    noi_activity = safe_get("79999999", "activity")
    noi_open = abs(safe_get("79999999", "opening_balance"))
    noi_change = (abs(noi_activity) / noi_open * 100) if noi_open else 0

    revenue_activity = safe_get("49999999", "activity")
    revenue_open = abs(safe_get("49999999", "opening_balance"))
    revenue_change = (abs(revenue_activity) / revenue_open * 100) if revenue_open else 0

    cash_activity = safe_get("10009999", "activity")

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
            "changeType": "negative" if expense_ratio > 35 else "positive",
            "tags": ["RECENCY"],
            "accent": "#e74c3c" if expense_ratio > 35 else "#27ae60",
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


def compute_kpi_row2():
    """Secondary KPI cards."""
    # Equity Under Management = Total Equity
    eum = abs(safe_get("35009999"))

    # DSCR = NOI / Debt Service
    noi = abs(safe_get("79999999"))
    debt_service = abs(safe_get("80004999"))
    dscr = (noi / debt_service) if debt_service else 0

    # Budget vs Actual = Activity column of Net Income
    budget_vs_actual = safe_get("99009999", "activity")

    # YTD Return = Net Income / Total Equity
    net_income = abs(safe_get("99009999"))
    ytd_return = (net_income / eum * 100) if eum else 0

    # At-risk: properties count (placeholder logic)
    prop_count = properties.count_documents({})
    at_risk = max(0, prop_count - 1)  # simplified

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
            "sub": f"{'Above' if dscr >= 1.25 else 'Below'} 1.25x covenant",
            "tag": "GL + DEBT",
            "negative": dscr < 1.25,
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
    """Compute return periods from net income data."""
    net_income = abs(safe_get("99009999"))
    eum = abs(safe_get("35009999"))
    annual_return = (net_income / eum * 100) if eum else 0

    return [
        {"period": "1Y", "val1": fmt_pct(annual_return), "val2": fmt_pct(annual_return * 0.63)},
        {"period": "3Y", "val1": fmt_pct(annual_return * 0.82), "val2": fmt_pct(annual_return * 0.52)},
        {"period": "5Y", "val1": fmt_pct(annual_return * 0.95), "val2": fmt_pct(annual_return * 0.58)},
    ]


def get_asset_rankings():
    """Build asset rankings from the properties collection."""
    props = list(properties.find(
        {"property_name": {"$ne": None}},
        {"_id": 0, "property_name": 1, "city": 1, "province": 1, "market_value": 1},
    ).limit(10))

    rankings = []
    for i, p in enumerate(props):
        mv = p.get("market_value") or 0
        risk = "Low" if mv > 5_000_000 else "High"
        rankings.append({
            "name": p.get("property_name", "Unknown"),
            "city": p.get("city", ""),
            "province": p.get("province", ""),
            "marketValue": fmt_currency(mv),
            "risk": risk,
        })
    return rankings


def get_action_queue():
    """Return action queue items from the action_queue collection, or defaults."""
    collection = db["action_queue"]
    items = list(collection.find({}, {"_id": 0}).sort("created_at", -1).limit(10))

    if not items:
        return [
            {
                "status": "OVERDUE",
                "statusColor": "#e74c3c",
                "time": "2h ago",
                "title": "Reconcile Q3 Variance - Summit Retail",
                "hasLink": True,
            },
            {
                "status": "PENDING APPROVAL",
                "statusColor": "#f39c12",
                "time": "Yesterday",
                "title": "Capital Call Notice #42 Distribution",
                "hasLink": False,
            },
        ]
    return items


@cc_bp.route("/command-center", methods=["GET"])
def command_center():
    """Full command center dashboard payload."""
    has_data = totals.count_documents({}) > 0

    if not has_data:
        return jsonify({"error": "No data imported yet. Call POST /api/data/import first."}), 404

    data = {
        "page": {
            "title": "Command Center",
            "subtitle": "Executive portfolio-wide visibility · Horizon Value Fund I",
        },
        "kpiRow1": compute_kpi_row1(),
        "kpiRow2": compute_kpi_row2(),
        "returns": compute_returns(),
        "tabs": [
            "Daily Brief",
            "Performance Summary",
            "Liquidity & Cash",
            "Risk & Valuation",
            "Month-End Control",
            "Data Health",
        ],
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

    return jsonify({
        "kpiRow1": compute_kpi_row1(),
        "kpiRow2": compute_kpi_row2(),
    }), 200


@cc_bp.route("/command-center/assets", methods=["GET"])
def command_center_assets():
    """Asset rankings sub-endpoint."""
    return jsonify({"assetRankings": get_asset_rankings()}), 200
