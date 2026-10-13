import os

import requests
from flask import Blueprint, jsonify, request

from ..db import get_db

ai_bp = Blueprint("ai", __name__)

# DEMO VULNERABILITY: hardcoded default API key (VULN-AI-001)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-demo-hardcoded-key-replace-me")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:5001")

# --- Split SDK (lazy init) ---------------------------------------------------
_split_client = None


def _get_split_client():
    global _split_client
    if _split_client is None:
        try:
            from splitio import get_factory

            factory = get_factory("v4kvjbb2cuupu0ihed20iceumvv1m9po07bn")
            factory.block_until_ready(5)
            _split_client = factory.client()
        except Exception:
            _split_client = None
    return _split_client


def _check_feature_flag():
    split = _get_split_client()
    treatment = split.get_treatment("demobank-user", "ai_chat_backend") if split else "on"
    return treatment == "on"


# --- Routes -------------------------------------------------------------------


@ai_bp.route("/chat", methods=["POST"])
def chat():
    if not _check_feature_flag():
        return jsonify({"error": "AI chat is currently disabled"}), 403

    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")
    if not user_message:
        return jsonify({"error": "message is required"}), 400

    db = get_db()
    accounts = [dict(r) for r in db.execute("SELECT * FROM accounts").fetchall()]
    transactions = [
        dict(r)
        for r in db.execute(
            "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10"
        ).fetchall()
    ]

    financial_context = {"accounts": accounts, "recent_transactions": transactions}

    # Enrich via MCP service
    mcp_data = {}
    try:
        mcp_resp = requests.post(
            f"{MCP_SERVER_URL}/enrich",
            json={"accounts": accounts, "query": user_message},
            timeout=5,
        )
        if mcp_resp.ok:
            mcp_data = mcp_resp.json()
    except Exception:
        pass

    # DEMO VULNERABILITY: prompt injection — user input concatenated directly (VULN-AI-002)
    base_prompt = (
        "You are DemoBank AI Assistant. Help users with their banking questions. "
        "Here is the customer financial data: " + str(financial_context) + ". "
        "MCP enrichment: " + str(mcp_data) + ". "
        "User question: " + user_message
    )

    try:
        import openai

        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": base_prompt}],
        )
        reply = completion.choices[0].message.content
    except Exception as e:
        reply = f"AI service unavailable: {e}"

    return jsonify(
        {
            "reply": reply,
            "financial_context": financial_context,
            "model": OPENAI_MODEL,
        }
    )


@ai_bp.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "model": OPENAI_MODEL,
            "mcp_server_url": MCP_SERVER_URL,
            "tools": ["account_lookup", "transaction_history", "mcp_enrich"],
            "status": "active",
        }
    )
