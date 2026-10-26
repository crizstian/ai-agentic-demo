"""MCP Financial Data Service — internal enrichment service for DemoBank.

Provides financial market data and risk profiles to DemoBank's AI assistant.
The AI assistant calls POST /api/enrich during chat interactions.

In the demo:
- Act 1: AI assistant calls this during /api/ai/chat
- Act 5: WAAP sees this as Este-Oeste (E-W) traffic inside the cluster
- Act 7: AI Discovery catalogs this as an MCP asset
"""

import os
from datetime import datetime

from flask import Flask, jsonify, request

app = Flask(__name__)

PORT = int(os.environ.get("MCP_PORT", 5001))

MARKET_DATA = {
    "interest_rates": {"savings": 4.25, "checking": 0.5, "cd_12mo": 5.1},
    "market_indices": {"sp500": 5432.10, "nasdaq": 17089.34, "dow": 39150.33},
    "forex": {"EUR_USD": 1.09, "GBP_USD": 1.27, "USD_JPY": 149.50},
}

RISK_PROFILES = {
    1: {"credit_score": 780, "risk_level": "low", "approved_limit": 50000},
    2: {"credit_score": 720, "risk_level": "medium", "approved_limit": 25000},
    3: {"credit_score": 810, "risk_level": "low", "approved_limit": 100000},
    4: {"credit_score": 690, "risk_level": "medium", "approved_limit": 15000},
    5: {"credit_score": 750, "risk_level": "low", "approved_limit": 75000},
}

PRODUCT_CATALOG = {
    "savings_premium": {
        "name": "Premium Savings",
        "min_balance": 10000,
        "apy": 4.25,
        "features": ["No monthly fee", "Free wire transfers", "Priority support"],
    },
    "cd_12mo": {
        "name": "12-Month CD",
        "min_deposit": 5000,
        "apy": 5.1,
        "early_withdrawal_penalty": "90 days interest",
    },
    "credit_platinum": {
        "name": "Platinum Credit Card",
        "credit_limit_range": [15000, 100000],
        "apr": 18.99,
        "rewards": "2% cashback on all purchases",
    },
}


def _build_enrichment(query, context=None):
    """Build enriched response combining market data with account context."""
    account_ids = []
    if context and "accounts" in context:
        account_ids = [a.get("id") for a in context["accounts"] if a.get("id")]

    relevant_profiles = {
        aid: RISK_PROFILES[aid] for aid in account_ids if aid in RISK_PROFILES
    }

    return {
        "source": "mcp-financial-data-service",
        "timestamp": datetime.utcnow().isoformat(),
        "query_received": query,
        "market_data": MARKET_DATA,
        "risk_profiles": relevant_profiles if relevant_profiles else None,
        "products": PRODUCT_CATALOG,
        "enrichment": {
            "type": "financial_context",
            "provider": "DemoBank Internal MCP",
            "data_classification": "CONFIDENTIAL",
            "tools_available": [
                "market_data_lookup",
                "risk_profile_check",
                "product_recommendation",
            ],
        },
    }


@app.route("/api/enrich", methods=["POST"])
def enrich():
    """Primary enrichment endpoint — called by DemoBank AI assistant."""
    body = request.get_json(silent=True) or {}
    query = body.get("query", "")
    context = body.get("context")
    return jsonify(_build_enrichment(query, context))


@app.route("/mcp/financial-data", methods=["POST"])
def financial_data():
    """Legacy MCP endpoint — kept for backward compatibility."""
    body = request.get_json(silent=True) or {}
    query = body.get("query", "")
    return jsonify(_build_enrichment(query))


@app.route("/mcp/risk-profile/<int:account_id>", methods=["GET"])
def risk_profile(account_id):
    """Return risk profile for a specific account."""
    profile = RISK_PROFILES.get(account_id)
    if not profile:
        return jsonify({"error": "Account not found"}), 404
    return jsonify({
        "account_id": account_id,
        "profile": profile,
        "source": "mcp-financial-data-service",
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "mcp-financial-data", "version": "1.1.0"})


if __name__ == "__main__":
    print(f"MCP Financial Data Service running on http://0.0.0.0:{PORT}")
    app.run(host="0.0.0.0", port=PORT)
