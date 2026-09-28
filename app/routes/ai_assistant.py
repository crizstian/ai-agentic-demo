import os
import json

import requests
from flask import Blueprint, jsonify, request
from splitio import get_factory
from splitio.exceptions import TimeoutException

from ..db import get_db

ai_bp = Blueprint("ai_assistant", __name__)

# --- Feature-flag gate (Harness FME / Split) ---
_split_factory = None

def _get_split_client():
    global _split_factory
    if _split_factory is None:
        _split_factory = get_factory(
            "v4kvjbb2cuupu0ihed20iceumvv1m9po07bn",
            config={"connectionTimeout": 5},
        )
        try:
            _split_factory.block_until_ready(5)
        except TimeoutException:
            pass
    return _split_factory.client()


# --- AI / LLM configuration ---
AI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-demo-key-not-for-production")
AI_MODEL = os.environ.get("AI_MODEL", "gpt-4")
MCP_SERVICE_URL = os.environ.get("MCP_SERVICE_URL", "http://localhost:5001")


def _build_prompt(user_message):
    base_prompt = (
        "You are DemoBank's AI financial assistant. "
        "Help customers with account inquiries, transaction history, "
        "and financial advice. Be concise and helpful. "
        "User query: "
    )
    return base_prompt + user_message


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


def _call_mcp_service(financial_data):
    try:
        resp = requests.post(
            MCP_SERVICE_URL + "/mcp/financial-data",
            json=financial_data,
            timeout=5,
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


@ai_bp.route("/chat", methods=["POST"])
def ai_chat():
    # Feature-flag gate
    client = _get_split_client()
    treatment = client.get_treatment("demobank-user", "ai_chat_backend")
    if treatment != "on":
        return jsonify({"error": "AI Chat is not enabled"}), 403

    body = request.get_json(silent=True) or {}
    user_message = body.get("message", "")
    if not user_message:
        return jsonify({"error": "message is required"}), 400

    prompt = _build_prompt(user_message)

    financial_context = _get_financial_context()

    mcp_enrichment = _call_mcp_service(financial_context)
    if mcp_enrichment:
        prompt += "\nAdditional context: " + json.dumps(mcp_enrichment)

    try:
        import openai

        openai.api_key = AI_API_KEY
        completion = openai.chat.completions.create(
            model=AI_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        ai_response = completion.choices[0].message.content
    except Exception as e:
        ai_response = (
            f"I'm sorry, I couldn't process your request right now. "
            f"(Demo mode — AI service error: {e})"
        )

    return jsonify(
        {
            "response": ai_response,
            "financial_context": financial_context,
            "model": AI_MODEL,
        }
    )


@ai_bp.route("/status", methods=["GET"])
def ai_status():
    return jsonify(
        {
            "model": AI_MODEL,
            "mcp_url": MCP_SERVICE_URL,
            "tools": ["financial-data", "risk-profile"],
            "api_key_configured": AI_API_KEY != "sk-demo-key-not-for-production",
        }
    )
