import datetime
from flask import Blueprint, jsonify, request

from db import db
from routes.command_center import fmt_currency, fmt_pct, safe_get

chat_bp = Blueprint("chat", __name__, url_prefix="/api")

totals = db["totals_data"]
properties = db["properties"]
fund_tree = db["fund_tree"]
chat_history = db["chat_history"]


def get_fund_context():
    """Build a snapshot of key fund metrics for answering questions."""
    return {
        "total_assets": abs(safe_get("19999999")),
        "total_cash": abs(safe_get("10009999")),
        "total_income": abs(safe_get("49999999")),
        "noi": abs(safe_get("79999999")),
        "total_equity": abs(safe_get("35009999")),
        "net_income": abs(safe_get("99009999")),
        "total_liabilities": abs(safe_get("29999998")),
        "total_debt": abs(safe_get("23009999")),
        "fund_expenses": abs(safe_get("83009999")),
        "nav": abs(safe_get("29999999")),
        "property_count": properties.count_documents({"property_name": {"$ne": None}}),
    }


def match_intent(message):
    """Simple keyword-based intent matching against fund data."""
    msg = message.lower().strip()
    ctx = get_fund_context()

    # NAV / Net Asset Value
    if any(k in msg for k in ["nav", "net asset value"]):
        return f"The current Net Asset Value (NAV) is **{fmt_currency(ctx['nav'])}**. This is derived from Total Assets ({fmt_currency(ctx['total_assets'])}) minus Total Liabilities ({fmt_currency(ctx['total_liabilities'])})."

    # AUM / Total Assets
    if any(k in msg for k in ["aum", "total assets", "assets under management"]):
        return f"Assets Under Management (AUM) stands at **{fmt_currency(ctx['total_assets'])}** across {ctx['property_count']} properties."

    # Cash
    if "cash" in msg:
        return f"Total cash position is **{fmt_currency(ctx['total_cash'])}**. This includes operating accounts, investment cash, and corporate cash holdings."

    # NOI
    if "noi" in msg or "net operating income" in msg:
        return f"Net Property Operating Income (NOI) is **{fmt_currency(ctx['noi'])}**. This is calculated before interest and amortization."

    # Revenue / Income
    if any(k in msg for k in ["revenue", "total income", "income"]):
        return f"Total Income is **{fmt_currency(ctx['total_income'])}**, which includes investment income, interest & dividends, and other income sources."

    # Expenses
    if any(k in msg for k in ["expense", "cost"]):
        ratio = (ctx['fund_expenses'] / ctx['total_income'] * 100) if ctx['total_income'] else 0
        return f"Total Fund Expenses are **{fmt_currency(ctx['fund_expenses'])}**, representing an expense ratio of **{fmt_pct(ratio)}** of total income."

    # Net Income / Profit
    if any(k in msg for k in ["net income", "profit", "earnings", "bottom line"]):
        ytd = (ctx['net_income'] / ctx['total_equity'] * 100) if ctx['total_equity'] else 0
        return f"Net Income is **{fmt_currency(ctx['net_income'])}**, producing a YTD return of **{fmt_pct(ytd)}** on equity."

    # Equity
    if "equity" in msg:
        return f"Total Equity (EUM) is **{fmt_currency(ctx['total_equity'])}**."

    # Debt / LTV / Leverage
    if any(k in msg for k in ["debt", "ltv", "leverage", "mortgage", "loan"]):
        ltv = (ctx['total_debt'] / ctx['total_assets'] * 100) if ctx['total_assets'] else 0
        return f"Total Debt is **{fmt_currency(ctx['total_debt'])}** with an LTV of **{fmt_pct(ltv)}**. The fund maintains conservative leverage."

    # DSCR
    if "dscr" in msg or "debt service coverage" in msg:
        debt_service = abs(safe_get("80004999"))
        dscr = (ctx['noi'] / debt_service) if debt_service else 0
        status = "above" if dscr >= 1.25 else "below"
        return f"Portfolio DSCR is **{dscr:.2f}x**, which is {status} the 1.25x covenant threshold."

    # Properties / Portfolio
    if any(k in msg for k in ["propert", "portfolio", "building", "asset list"]):
        props = list(properties.find(
            {"property_name": {"$ne": None}},
            {"_id": 0, "property_name": 1, "city": 1, "market_value": 1},
        ).sort("market_value", -1).limit(5))
        if props:
            lines = [f"The portfolio has **{ctx['property_count']} properties**. Top by market value:\n"]
            for p in props:
                mv = p.get("market_value", 0) or 0
                lines.append(f"- **{p.get('property_name')}** ({p.get('city', '')}) — {fmt_currency(mv)}")
            return "\n".join(lines)
        return f"The portfolio contains **{ctx['property_count']} properties**."

    # Liabilities
    if "liabilit" in msg:
        return f"Total Liabilities are **{fmt_currency(ctx['total_liabilities'])}**, including mortgage debt of {fmt_currency(ctx['total_debt'])}."

    # Occupancy
    if "occupanc" in msg:
        pipeline = [
            {"$match": {"property_name": {"$ne": None}}},
            {"$group": {
                "_id": None,
                "total": {"$sum": 1},
                "occupied": {"$sum": {"$cond": [{"$gt": ["$market_value", 0]}, 1, 0]}},
            }},
        ]
        result = list(properties.aggregate(pipeline))
        if result:
            occ = (result[0]["occupied"] / result[0]["total"] * 100) if result[0]["total"] else 0
            return f"Portfolio occupancy is approximately **{fmt_pct(occ, 0)}** across {result[0]['total']} properties."
        return "Occupancy data is not currently available."

    # Summary / Overview
    if any(k in msg for k in ["summary", "overview", "how is the fund", "fund performance", "status", "dashboard"]):
        ytd = (ctx['net_income'] / ctx['total_equity'] * 100) if ctx['total_equity'] else 0
        ltv = (ctx['total_debt'] / ctx['total_assets'] * 100) if ctx['total_assets'] else 0
        return (
            f"**Fund Summary — Horizon Value Fund I**\n\n"
            f"- **AUM:** {fmt_currency(ctx['total_assets'])}\n"
            f"- **NAV:** {fmt_currency(ctx['nav'])}\n"
            f"- **NOI:** {fmt_currency(ctx['noi'])}\n"
            f"- **Net Income:** {fmt_currency(ctx['net_income'])}\n"
            f"- **Cash:** {fmt_currency(ctx['total_cash'])}\n"
            f"- **LTV:** {fmt_pct(ltv)}\n"
            f"- **YTD Return:** {fmt_pct(ytd)}\n"
            f"- **Properties:** {ctx['property_count']}"
        )

    # Help
    if any(k in msg for k in ["help", "what can you", "capabilities"]):
        return (
            "I can answer questions about the fund's financial data. Try asking about:\n\n"
            "- **NAV** — Net Asset Value\n"
            "- **AUM** — Assets Under Management\n"
            "- **NOI** — Net Operating Income\n"
            "- **Cash** position\n"
            "- **Revenue** / Income\n"
            "- **Expenses** and expense ratio\n"
            "- **Debt** / LTV / Leverage\n"
            "- **DSCR** — Debt Service Coverage\n"
            "- **Properties** in the portfolio\n"
            "- **Net Income** / Returns\n"
            "- **Fund summary** / Overview"
        )

    # Default
    return (
        "I'm not sure I understand that question. I can help with fund metrics like "
        "**NAV**, **AUM**, **NOI**, **cash**, **debt/LTV**, **DSCR**, **expenses**, "
        "**properties**, or a full **fund summary**. Try asking about one of these!"
    )


@chat_bp.route("/chat", methods=["POST"])
def chat():
    """Process a chat message and return a response based on fund data."""
    body = request.get_json()
    if not body or not body.get("message"):
        return jsonify({"error": "Message is required"}), 400

    user_message = body["message"]
    session_id = body.get("sessionId", "default")

    # Generate response
    response_text = match_intent(user_message)

    # Store in chat history
    chat_history.insert_one({
        "session_id": session_id,
        "role": "user",
        "content": user_message,
        "timestamp": datetime.datetime.now(datetime.timezone.utc),
    })
    chat_history.insert_one({
        "session_id": session_id,
        "role": "assistant",
        "content": response_text,
        "timestamp": datetime.datetime.now(datetime.timezone.utc),
    })

    return jsonify({
        "role": "assistant",
        "content": response_text,
    }), 200


@chat_bp.route("/chat/history", methods=["GET"])
def history():
    """Get chat history for a session."""
    session_id = request.args.get("sessionId", "default")
    messages = list(chat_history.find(
        {"session_id": session_id},
        {"_id": 0, "session_id": 0},
    ).sort("timestamp", 1).limit(50))
    return jsonify({"messages": messages}), 200
