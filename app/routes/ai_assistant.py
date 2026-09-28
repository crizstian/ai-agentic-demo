import os

import requests
from flask import Blueprint, jsonify, request

from ..db import get_db

ai_bp = Blueprint("ai_assistant", __name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-demo-default-key-1234567890")
OPENAI_MODEL = "gpt-4"
MCP_SERVICE_URL = os.environ.get("MCP_SERVICE_URL", "http://localhost:5001")

SYSTEM_PROMPT = """You are DemoBank AI Assistant, a helpful banking assistant.
You help customers with account inquiries, transaction history, and financial advice.
Here is the customer context: """


def _get_feature_flag_treatment():
    from splitio import get_factory

    factory = get_factory("v4kvjbb2cuupu0ihed20iceumvv1m9po07bn")
    factory.block_until_ready(5)
    client = factory.client()
    treatment = client.get_treatment("demobank-user", "ai_chat_backend")
    return treatment


def _query_account_data():
    db = get_db()
    accounts = [dict(r) for r in db.execute("SELECT * FROM accounts").fetchall()]
    transactions = [
        dict(r)
        for r in db.execute(
            "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10"
        ).fetchall()
    ]
    return {"accounts": accounts, "transactions": transactions}


def _enrich_with_mcp(financial_data):
    try:
        resp = requests.post(
            MCP_SERVICE_URL + "/enrich",
            json=financial_data,
            timeout=5,
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return financial_data


@ai_bp.route("/chat", methods=["POST"])
def chat():
    treatment = _get_feature_flag_treatment()
    if treatment != "on":
        return jsonify({"error": "AI Chat is not enabled"}), 403

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "message is required"}), 400

    user_message = data["message"]
    financial_data = _query_account_data()
    enriched_data = _enrich_with_mcp(financial_data)

    prompt = SYSTEM_PROMPT + user_message

    try:
        import openai

        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_message},
            ],
        )
        ai_response = response.choices[0].message.content
    except Exception as e:
        ai_response = f"AI service temporarily unavailable: {str(e)}"

    return jsonify(
        {
            "response": ai_response,
            "financial_context": enriched_data,
        }
    )


@ai_bp.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "model": OPENAI_MODEL,
            "mcp_url": MCP_SERVICE_URL,
            "tools": ["account_lookup", "transaction_history", "financial_enrichment"],
            "api_key_configured": bool(os.environ.get("OPENAI_API_KEY")),
        }
    )
