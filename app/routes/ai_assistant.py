import json
import os

import requests
from flask import Blueprint, jsonify, request
from splitio import get_factory

from ..db import get_db

ai_bp = Blueprint("ai", __name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-demo-key-replace-me")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:5001")

SYSTEM_PROMPT = """You are DemoBank's AI financial assistant. You help customers with:
- Account balances and transaction history
- Transfer guidance and payment help
- General banking questions

Be concise, professional, and helpful. If you don't have specific data,
say so rather than making up numbers."""

_split_client = None


def _get_split_client():
    global _split_client
    if _split_client is None:
        try:
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


def _enrich_via_mcp(message, financial_data):
    try:
        resp = requests.post(
            f"{MCP_SERVER_URL}/enrich",
            json={"message": message, "context": financial_data},
            timeout=5,
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


@ai_bp.route("/chat", methods=["POST"])
def chat():
    if not _check_feature_flag():
        return jsonify({"error": "AI chat is currently disabled"}), 403

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "message field is required"}), 400

    user_message = data["message"]
    financial_data = _get_financial_context()

    mcp_enrichment = _enrich_via_mcp(user_message, financial_data)

    prompt = SYSTEM_PROMPT + "\n\nUser financial data: " + json.dumps(financial_data) + "\n\nUser message: " + user_message

    try:
        import openai

        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=512,
        )
        ai_response = completion.choices[0].message.content
    except Exception as e:
        ai_response = f"I'm sorry, I'm having trouble connecting to the AI service right now. Error: {str(e)}"

    return jsonify(
        {
            "response": ai_response,
            "financial_context": financial_data,
            "mcp_enrichment": mcp_enrichment,
        }
    )


@ai_bp.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "model": OPENAI_MODEL,
            "mcp_url": MCP_SERVER_URL,
            "tools": ["account_lookup", "transaction_history", "transfer_guidance"],
        }
    )
