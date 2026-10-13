import os

import requests
from flask import Blueprint, jsonify, request
from openai import OpenAI

from ..db import get_db

ai_bp = Blueprint("ai_assistant", __name__)

# DEMO VULNERABILITY: hardcoded default API key (VULN-008)
DEFAULT_API_KEY = "sk-demo-default-key-1234567890"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", DEFAULT_API_KEY)
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:5001")

client = OpenAI(api_key=OPENAI_API_KEY)

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
    treatment = split.get_treatment("demobank-server", "ai_chat_backend") if split else "on"
    return treatment == "on"


# --- Routes -------------------------------------------------------------------


@ai_bp.route("/chat", methods=["POST"])
def chat():
    if not _check_feature_flag():
        return jsonify({"error": "AI chat feature is disabled"}), 403

    data = request.get_json(force=True)
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    db = get_db()
    accounts = [dict(r) for r in db.execute("SELECT * FROM accounts").fetchall()]
    transactions = [
        dict(r)
        for r in db.execute(
            "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10"
        ).fetchall()
    ]

    financial_context = {"accounts": accounts, "transactions": transactions}

    # DEMO VULNERABILITY: prompt injection — user input concatenated directly (VULN-009)
    base_prompt = (
        "You are DemoBank AI Assistant. You help customers with their banking needs. "
        "Here is the customer financial data: " + str(financial_context) + "\n\n"
        "Customer message: " + user_message
    )

    # Enrich via MCP service
    mcp_enrichment = None
    try:
        mcp_resp = requests.post(
            f"{MCP_SERVER_URL}/enrich",
            json={"message": user_message, "context": financial_context},
            timeout=3,
        )
        if mcp_resp.ok:
            mcp_enrichment = mcp_resp.json()
            base_prompt += "\n\nAdditional context from MCP: " + str(mcp_enrichment)
    except Exception:
        pass

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": base_prompt}],
            max_tokens=512,
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"I apologize, I'm having trouble connecting to the AI service. Error: {str(e)}"

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
            "mcp_server_url": MCP_SERVER_URL,
            "tools": ["account_lookup", "transaction_history", "mcp_enrich"],
            "api_key_source": "env" if os.environ.get("OPENAI_API_KEY") else "default",
        }
    )
