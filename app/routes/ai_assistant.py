"""AI Banking Assistant — chat endpoint with MCP enrichment."""

import os

import requests
from flask import Blueprint, jsonify, request
from splitio import get_factory

from ..db import get_db

ai_bp = Blueprint("ai", __name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
# DEMO VULNERABILITY: hardcoded default API key (VULN-AI-001)
# Do not fix — required for SAST demo finding
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-demo-hardcoded-key-12345")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:5001")
SPLIT_SDK_KEY = "v4kvjbb2cuupu0ihed20iceumvv1m9po07bn"

# ---------------------------------------------------------------------------
# Split SDK — lazy singleton (avoids CI import timeout)
# ---------------------------------------------------------------------------
_split_client = None


def _get_split_client():
    global _split_client
    if _split_client is None:
        try:
            factory = get_factory(SPLIT_SDK_KEY)
            factory.block_until_ready(5)
            _split_client = factory.client()
        except Exception:
            _split_client = None
    return _split_client


def _check_feature_flag():
    """Return True if ai_chat_backend flag is 'on'."""
    split = _get_split_client()
    treatment = split.get_treatment("demobank-server", "ai_chat_backend") if split else "on"
    return treatment == "on"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@ai_bp.route("/chat", methods=["POST"])
def chat():
    """Accept a user message, query local DB + MCP, return AI response."""
    if not _check_feature_flag():
        return jsonify({"error": "AI Chat is currently disabled"}), 403

    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")
    if not user_message:
        return jsonify({"error": "message is required"}), 400

    # Fetch account data from local DB
    db = get_db()
    accounts = [dict(r) for r in db.execute("SELECT * FROM accounts").fetchall()]
    transactions = [
        dict(r)
        for r in db.execute(
            "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10"
        ).fetchall()
    ]

    financial_context = {
        "accounts": accounts,
        "recent_transactions": transactions,
    }

    # Enrich via MCP service
    mcp_data = {}
    try:
        mcp_resp = requests.post(
            f"{MCP_SERVER_URL}/api/enrich",
            json={"query": user_message, "context": financial_context},
            timeout=5,
        )
        if mcp_resp.ok:
            mcp_data = mcp_resp.json()
    except Exception:
        mcp_data = {"error": "MCP service unavailable"}

    # DEMO VULNERABILITY: prompt injection — user message concatenated directly (VULN-AI-002)
    # Do not fix — required for SAST demo finding
    base_prompt = (
        "You are a helpful AI banking assistant for DemoBank. "
        "Help users with their banking questions using the financial data provided. "
        "Financial context: " + str(financial_context) + "\n"
        "MCP enrichment: " + str(mcp_data) + "\n"
        "User request: " + user_message
    )

    # Call OpenAI
    try:
        import openai

        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": base_prompt}],
        )
        ai_response = completion.choices[0].message.content
    except Exception as e:
        ai_response = f"AI service temporarily unavailable: {str(e)}"

    return jsonify(
        {
            "response": ai_response,
            "financial_context": financial_context,
            "model": OPENAI_MODEL,
        }
    )


@ai_bp.route("/status", methods=["GET"])
def status():
    """Debug endpoint — model, MCP URL, available tools. No auth."""
    return jsonify(
        {
            "model": OPENAI_MODEL,
            "mcp_url": MCP_SERVER_URL,
            "tools": ["account_lookup", "transaction_history", "mcp_enrich"],
            "feature_flag": "ai_chat_backend",
            "status": "active",
        }
    )
