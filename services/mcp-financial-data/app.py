"""MCP Financial Data Service — mock internal service for DemoBank demo.

Simulates an MCP tool that provides financial data enrichment.
DemoBank's AI assistant calls this service for additional context.

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


@app.route("/mcp/financial-data", methods=["POST"])
def financial_data():
    """MCP tool endpoint — returns enriched financial context.

    This is the endpoint that DemoBank's AI assistant calls internally.
    In Act 5, WAAP monitors this Este-Oeste traffic and detects anomalies
    when the prompt injection payload travels through this call.
    """
    body = request.get_json(silent=True) or {}
    query = body.get("query", "")

    return jsonify({
        "source": "mcp-financial-data-service",
        "timestamp": datetime.utcnow().isoformat(),
        "query_received": query,
        "market_data": MARKET_DATA,
        "enrichment": {
            "type": "financial_context",
            "provider": "DemoBank Internal MCP",
            "data_classification": "CONFIDENTIAL",
        },
    })


@app.route("/mcp/risk-profile/<int:account_id>", methods=["GET"])
def risk_profile(account_id):
    """Return risk profile for an account — additional MCP tool."""
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
    return jsonify({"status": "ok", "service": "mcp-financial-data"})


if __name__ == "__main__":
    print(f"MCP Financial Data Service running on http://0.0.0.0:{PORT}")
    app.run(host="0.0.0.0", port=PORT)
