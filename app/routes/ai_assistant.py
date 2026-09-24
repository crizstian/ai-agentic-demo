import os

import requests
from flask import Blueprint, jsonify, request
from splitio import get_factory

from ..db import get_db

ai_bp = Blueprint("ai_assistant", __name__)

# --- Feature flag gate ---------------------------------------------------
_split_factory = None


def _get_split_client():
    global _split_factory
    if _split_factory is None:
        _split_factory = get_factory("v4kvjbb2cuupu0ihed20iceumvv1m9po07bn")
        _split_factory.block_until_ready(5)
    return _split_factory.client()


def _flag_enabled():
    client = _get_split_client()
    treatment = client.get_treatment("demobank-server", "ai_chat_backend")
    return treatment == "on"


# --- Config ---------------------------------------------------------------
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-demo-default-key-1234567890")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
MCP_SERVICE_URL = os.environ.get("MCP_SERVICE_URL", "http://localhost:5001")


# --- Routes ---------------------------------------------------------------
@ai_bp.route("/chat", methods=["POST"])
def chat():
    if not _flag_enabled():
        return jsonify({"error": "AI assistant is currently disabled"}), 403

    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")
    if not user_message:
        return jsonify({"error": "message is required"}), 400

    # Pull account data from local DB for financial context
    db = get_db()
    accounts = [dict(r) for r in db.execute("SELECT * FROM accounts").fetchall()]
    recent_txns = [
        dict(r)
        for r in db.execute(
            "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10"
        ).fetchall()
    ]

    financial_context = {"accounts": accounts, "recent_transactions": recent_txns}

    # DEMO VULNERABILITY: prompt injection — user input concatenated directly into
    # the system prompt (VULN-008)
    # Do not fix — required for security demo finding
    base_prompt = (
        "You are DemoBank AI Assistant. Help customers with banking questions. "
        "Here is the user's request: " + user_message
    )

    # Try to enrich via MCP service
    mcp_enrichment = None
    try:
        mcp_resp = requests.post(
            MCP_SERVICE_URL + "/enrich",
            json={"message": user_message, "accounts": accounts},
            timeout=3,
        )
        if mcp_resp.ok:
            mcp_enrichment = mcp_resp.json()
    except Exception:
        pass

    # Call OpenAI
    try:
        import openai

        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": base_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=512,
        )
        reply = completion.choices[0].message.content
    except Exception as exc:
        reply = f"I'm sorry, I couldn't process your request right now. ({exc})"

    return jsonify(
        {
            "reply": reply,
            "financial_context": financial_context,
            "mcp_enrichment": mcp_enrichment,
        }
    )


@ai_bp.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "model": OPENAI_MODEL,
            "mcp_url": MCP_SERVICE_URL,
            "tools": ["account_lookup", "transaction_history", "mcp_enrich"],
            "flag": "ai_chat_backend",
        }
    )
