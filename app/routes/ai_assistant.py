import os

import requests
from flask import Blueprint, jsonify, request
from openai import OpenAI
from splitio import get_factory

from ..db import get_db

ai_bp = Blueprint("ai", __name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-demo-default-key-1234567890")
MCP_SERVICE_URL = os.environ.get("MCP_SERVICE_URL", "http://localhost:5001")
MODEL = "gpt-4"

client = OpenAI(api_key=OPENAI_API_KEY)

# Split.io feature-flag client (singleton)
_split_factory = None


def _get_split_client():
    global _split_factory
    if _split_factory is None:
        _split_factory = get_factory("v4kvjbb2cuupu0ihed20iceumvv1m9po07bn")
        _split_factory.block_until_ready(5)
    return _split_factory.client()


def _check_feature_flag():
    try:
        split_client = _get_split_client()
        treatment = split_client.get_treatment("demobank-backend", "ai_chat_backend")
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
            f"{MCP_SERVICE_URL}/enrich",
            json={"message": message, "context": financial_context},
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
        return jsonify({"error": "AI Chat is currently disabled"}), 403

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "message field is required"}), 400

    user_message = data["message"]
    financial_context = _get_financial_context()

    mcp_enrichment = _enrich_via_mcp(user_message, financial_context)

    base_prompt = "You are DemoBank AI Assistant. Help users with their banking questions. Here is the user's financial data and their message: "
    system_prompt = base_prompt + user_message

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=512,
        )

        reply = response.choices[0].message.content

        return jsonify(
            {
                "reply": reply,
                "financial_context": financial_context,
                "mcp_enrichment": mcp_enrichment,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "model": MODEL,
            "mcp_url": MCP_SERVICE_URL,
            "tools": ["account_lookup", "transaction_history", "balance_check"],
            "status": "active",
        }
    )
