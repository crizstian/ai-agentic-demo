import os

import requests
from flask import Blueprint, jsonify, request

ai_bp = Blueprint("ai", __name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-demo-key-replace-me")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://mcp-financial-data:5001")

_split_client = None


def _get_split_client():
    global _split_client
    if _split_client is None:
        from splitio import get_factory

        factory = get_factory("v4kvjbb2cuupu0ihed20iceumvv1m9po07bn")
        factory.block_until_ready(5)
        _split_client = factory.client()
    return _split_client


def _check_feature_flag():
    try:
        client = _get_split_client()
        treatment = client.get_treatment("demobank-backend", "ai_chat_backend")
        return treatment == "on"
    except Exception:
        return True


def _get_account_data():
    from ..db import get_db

    db = get_db()
    accounts = [dict(r) for r in db.execute("SELECT * FROM accounts").fetchall()]
    return accounts


def _enrich_with_mcp(query, accounts):
    try:
        account_ids = [{"id": a["id"]} for a in accounts]
        resp = requests.post(
            f"{MCP_SERVER_URL}/api/enrich",
            json={"query": query, "context": {"accounts": account_ids}},
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

    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")
    if not user_message:
        return jsonify({"error": "message is required"}), 400

    accounts = _get_account_data()
    financial_context = _enrich_with_mcp(user_message, accounts)

    base_prompt = (
        "You are DemoBank's AI assistant. Help customers with their banking needs. "
        "Here are the customer's accounts: " + str(accounts) + ". "
        "User question: " + user_message
    )

    try:
        import openai

        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": base_prompt}],
        )
        ai_response = completion.choices[0].message.content
    except Exception as e:
        ai_response = f"I'm sorry, I couldn't process your request right now. Error: {str(e)}"

    return jsonify(
        {
            "response": ai_response,
            "financial_context": financial_context,
            "model": OPENAI_MODEL,
        }
    )


@ai_bp.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "model": OPENAI_MODEL,
            "mcp_url": MCP_SERVER_URL,
            "tools": ["market_data_lookup", "risk_profile_check", "product_recommendation"],
        }
    )
