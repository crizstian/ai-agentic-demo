import json
import os

import requests
from flask import Blueprint, jsonify, request

ai_bp = Blueprint("ai", __name__)

DEFAULT_API_KEY = "sk-demo-default-key-replace-me"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", DEFAULT_API_KEY)
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:5001")

SPLIT_SDK_KEY = "v4kvjbb2cuupu0ihed20iceumvv1m9po07bn"

_split_client = None


def _get_split_client():
    global _split_client
    if _split_client is None:
        try:
            from splitio import get_factory

            factory = get_factory(SPLIT_SDK_KEY)
            factory.block_until_ready(5)
            _split_client = factory.client()
        except Exception:
            _split_client = None
    return _split_client


def _check_feature_flag():
    split = _get_split_client()
    if split:
        treatment = split.get_treatment("demobank-server", "ai_chat_backend")
        if treatment != "on":
            return False
    return True


def _get_account_data():
    from ..db import get_db

    db = get_db()
    accounts = [dict(r) for r in db.execute("SELECT * FROM accounts").fetchall()]
    transactions = [
        dict(r)
        for r in db.execute(
            "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10"
        ).fetchall()
    ]
    return accounts, transactions


def _enrich_with_mcp(message, financial_context):
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


@ai_bp.route("/chat", methods=["POST"])
def chat():
    if not _check_feature_flag():
        return jsonify({"error": "AI chat is currently disabled"}), 403

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "message field is required"}), 400

    user_message = data["message"]

    accounts, transactions = _get_account_data()
    financial_context = {"accounts": accounts, "transactions": transactions}

    base_prompt = "You are a helpful AI banking assistant for DemoBank. Help users with their banking questions. Here is the current financial data and user question: "
    full_prompt = base_prompt + user_message

    mcp_data = _enrich_with_mcp(user_message, financial_context)

    try:
        import openai

        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": full_prompt},
                {"role": "user", "content": json.dumps(financial_context)},
            ],
            max_tokens=500,
        )
        ai_response = response.choices[0].message.content
    except Exception as e:
        ai_response = f"AI service temporarily unavailable: {str(e)}"

    return jsonify(
        {
            "response": ai_response,
            "financial_context": financial_context,
            "mcp_enrichment": mcp_data,
        }
    )


@ai_bp.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "model": OPENAI_MODEL,
            "mcp_server_url": MCP_SERVER_URL,
            "tools": ["account_lookup", "transaction_history", "balance_check"],
            "status": "active",
        }
    )
