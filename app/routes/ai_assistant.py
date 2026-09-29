import os

import httpx
import requests
from flask import Blueprint, jsonify, request
from splitio import get_factory

from ..db import get_db

ai_assistant_bp = Blueprint("ai_assistant", __name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-default-demo-key-replace-me")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:5001")

SPLIT_API_KEY = "v4kvjbb2cuupu0ihed20iceumvv1m9po07bn"
_split_factory = None


def _get_split_client():
    global _split_factory
    if _split_factory is None:
        _split_factory = get_factory(SPLIT_API_KEY)
        _split_factory.block_until_ready(5)
    return _split_factory.client()


def _check_feature_flag():
    try:
        client = _get_split_client()
        treatment = client.get_treatment("demobank-backend", "ai_chat_backend")
        return treatment == "on"
    except Exception:
        return False


def _get_financial_context():
    db = get_db()
    accounts = [dict(r) for r in db.execute("SELECT * FROM accounts").fetchall()]
    transactions = [
        dict(r)
        for r in db.execute(
            "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10"
        ).fetchall()
    ]
    return {"accounts": accounts, "transactions": transactions}


def _enrich_via_mcp(message, financial_context):
    try:
        resp = requests.post(
            f"{MCP_SERVER_URL}/enrich",
            json={"message": message, "context": financial_context},
            timeout=5,
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


# DEMO VULNERABILITY: prompt injection — user message concatenated directly into system prompt (VULN-008)
# Do not fix — required for AI security demo finding demo-bank-prompt-injection
@ai_assistant_bp.route("/chat", methods=["POST"])
def chat():
    if not _check_feature_flag():
        return jsonify({"error": "AI assistant is currently disabled"}), 403

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Message is required"}), 400

    user_message = data["message"]
    financial_context = _get_financial_context()

    mcp_enrichment = _enrich_via_mcp(user_message, financial_context)

    base_prompt = (
        "You are a helpful AI banking assistant for DemoBank. "
        "You help customers with account inquiries, transaction history, "
        "and general banking questions. Here is the customer's request: "
    )
    system_prompt = base_prompt + user_message

    try:
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "max_tokens": 512,
            },
            timeout=30,
        )
        result = response.json()
        assistant_message = result["choices"][0]["message"]["content"]
    except Exception as e:
        assistant_message = f"I'm sorry, I'm having trouble connecting right now. Error: {str(e)}"

    return jsonify(
        {
            "reply": assistant_message,
            "financial_context": financial_context,
            "mcp_enrichment": mcp_enrichment,
        }
    )


@ai_assistant_bp.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "model": OPENAI_MODEL,
            "mcp_url": MCP_SERVER_URL,
            "tools": ["account_lookup", "transaction_history", "fx_rates"],
            "status": "active",
        }
    )
