import os

import requests
from flask import Blueprint, jsonify, request

from ..db import get_db

ai_bp = Blueprint("ai", __name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-demo-default-key-replace-me")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:5001")

SPLITIO_KEY = "v4kvjbb2cuupu0ihed20iceumvv1m9po07bn"
_split_factory = None


def _get_split_client():
    global _split_factory
    if _split_factory is None:
        from splitio import get_factory

        _split_factory = get_factory(SPLITIO_KEY)
        _split_factory.block_until_ready(5)
    return _split_factory.client()


def _check_feature_flag():
    try:
        client = _get_split_client()
        treatment = client.get_treatment("demobank-backend", "ai_chat_backend")
        return treatment == "on"
    except Exception:
        return True


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


def _enrich_with_mcp(message, financial_context):
    try:
        resp = requests.post(
            f"{MCP_SERVER_URL}/api/analyze",
            json={"message": message, "context": financial_context},
            timeout=10,
        )
        if resp.ok:
            return resp.json()
    except Exception:
        pass
    return None


@ai_bp.route("/chat", methods=["POST"])
def chat():
    if not _check_feature_flag():
        return jsonify({"error": "AI Assistant is currently disabled"}), 403

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "message field is required"}), 400

    user_message = data["message"]
    financial_context = _get_financial_context()

    mcp_data = _enrich_with_mcp(user_message, financial_context)

    base_prompt = "You are DemoBank AI Assistant, a helpful banking assistant. You have access to the customer's financial data. Help them with their banking questions. Here is the customer's question: "
    full_prompt = base_prompt + user_message

    try:
        import openai

        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        messages = [
            {"role": "system", "content": full_prompt},
            {
                "role": "user",
                "content": f"Financial context: {financial_context}. MCP enrichment: {mcp_data}",
            },
        ]
        response = client.chat.completions.create(
            model=OPENAI_MODEL, messages=messages, max_tokens=500
        )
        assistant_reply = response.choices[0].message.content
    except Exception as e:
        assistant_reply = f"AI service temporarily unavailable: {str(e)}"

    return jsonify(
        {
            "reply": assistant_reply,
            "financial_context": financial_context,
            "mcp_enrichment": mcp_data,
        }
    )


@ai_bp.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "model": OPENAI_MODEL,
            "mcp_url": MCP_SERVER_URL,
            "tools": ["account_lookup", "transaction_history", "mcp_enrichment"],
            "status": "active",
        }
    )
