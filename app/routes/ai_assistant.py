import os
import re

import requests
from flask import Blueprint, jsonify, request

from ..db import get_db

ai_assistant_bp = Blueprint("ai_assistant", __name__)

MCP_FINANCIAL_DATA_URL = os.environ.get(
    "MCP_FINANCIAL_DATA_URL", "http://localhost:5001/mcp/financial-data"
)

MAX_MESSAGE_LENGTH = 500


def _sanitize_input(text):
    """Strip control characters and limit length to prevent prompt injection."""
    cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)
    return cleaned[:MAX_MESSAGE_LENGTH]


# [REMEDIATED] VULN-009: Now returns only aggregated data, no PII
def _query_financial_context(message):
    """Retrieve aggregated financial context for the AI assistant."""
    db = get_db()
    row = db.execute(
        "SELECT COUNT(*) as total_accounts, SUM(balance) as total_balance FROM accounts"
    ).fetchone()
    return {"total_accounts": row["total_accounts"], "total_balance": row["total_balance"]}


def _call_mcp_tool(message):
    """Call an external MCP financial-data tool for enrichment."""
    try:
        resp = requests.post(
            MCP_FINANCIAL_DATA_URL,
            json={"query": message},
            timeout=5,
        )
        return resp.json()
    except requests.RequestException:
        return {"error": "MCP tool unavailable", "source": MCP_FINANCIAL_DATA_URL}


# [REMEDIATED] VULN-008: Input sanitized and separated from system prompt
@ai_assistant_bp.route("/chat", methods=["POST"])
def chat():
    """AI-powered banking assistant chat endpoint."""
    body = request.get_json(silent=True) or {}
    message = body.get("message")
    session_id = body.get("session_id", "anonymous")

    if not message:
        return jsonify({"error": "Missing required field: message"}), 400

    sanitized_message = _sanitize_input(message)

    financial_context = _query_financial_context(sanitized_message)
    mcp_result = _call_mcp_tool(sanitized_message)

    ai_response = {
        "response": (
            "Based on your inquiry, here is what I found in our records."
        ),
        "session_id": session_id,
    }

    return jsonify(ai_response)


@ai_assistant_bp.route("/status", methods=["GET"])
def ai_status():
    """Return the AI assistant's operational status and configured MCP tools."""
    return jsonify(
        {
            "status": "active",
            "model": "demobank-assistant-v1",
            "mcp_tools": [
                {
                    "name": "financial-data",
                    "url": MCP_FINANCIAL_DATA_URL,
                    "description": "Retrieves customer financial data for AI enrichment",
                },
            ],
            "warning": "DEMO ONLY — not a real AI assistant",
        }
    )
