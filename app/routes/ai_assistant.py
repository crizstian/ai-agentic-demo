import os

import requests
from flask import Blueprint, jsonify, request

from ..db import get_db

ai_assistant_bp = Blueprint("ai_assistant", __name__)

MCP_FINANCIAL_DATA_URL = os.environ.get(
    "MCP_FINANCIAL_DATA_URL", "http://localhost:5001/mcp/financial-data"
)


# DEMO VULNERABILITY: AI response leaks PII/sensitive financial data (VULN-009)
def _query_financial_context(message):
    """Simulate an MCP tool / RAG retrieval that fetches account data for the AI.

    Returns raw account rows including owner names and balances — no PII
    filtering is applied before the data is surfaced in the AI response.
    """
    db = get_db()
    rows = db.execute(
        "SELECT id, owner, balance, type FROM accounts"
    ).fetchall()
    return [dict(r) for r in rows]


def _call_mcp_tool(message):
    """Call an external MCP financial-data tool for enrichment.

    This simulates Layer 3 of the AI security model — an AI agent calling
    an MCP tool.  Runtime Protection Agent monitors this traffic.
    """
    try:
        resp = requests.post(
            MCP_FINANCIAL_DATA_URL,
            json={"query": message},
            timeout=5,
        )
        return resp.json()
    except requests.RequestException:
        return {"error": "MCP tool unavailable", "source": MCP_FINANCIAL_DATA_URL}


# DEMO VULNERABILITY: prompt injection — user input concatenated into system prompt (VULN-008)
@ai_assistant_bp.route("/chat", methods=["POST"])
def chat():
    """AI-powered banking assistant chat endpoint.

    Accepts a user message and returns a mock AI response enriched with
    financial context retrieved from internal data sources and an external
    MCP tool.
    """
    body = request.get_json(silent=True) or {}
    message = body.get("message")
    session_id = body.get("session_id", "anonymous")

    if not message:
        return jsonify({"error": "Missing required field: message"}), 400

    # VULN-008: user input is concatenated directly into the system prompt
    # without any sanitisation, enabling prompt injection attacks.
    system_prompt = (
        "You are DemoBank's AI financial assistant. "
        "Answer the customer's question using the provided context.\n\n"
        "Customer message: " + message
    )

    # Retrieve financial context (simulated RAG / MCP tool call)
    financial_context = _query_financial_context(message)

    # Call external MCP tool for additional enrichment
    mcp_result = _call_mcp_tool(message)

    # Build mock AI response — includes raw financial context (VULN-009)
    ai_response = {
        "response": (
            "Based on your inquiry, here is what I found in our records."
        ),
        "session_id": session_id,
        "system_prompt_used": system_prompt,
        "financial_context": financial_context,
        "mcp_tool_result": mcp_result,
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
