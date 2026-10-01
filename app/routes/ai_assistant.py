import os

import httpx
import requests
from flask import Blueprint, jsonify, request

from ..db import get_db

ai_assistant_bp = Blueprint("ai_assistant", __name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-default-demo-key-replace-me")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
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
        treatment = split.get_treatment("demobank-user", "ai_chat_backend")
        return treatment == "on"
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


# DEMO VULNERABILITY: prompt injection — user input concatenated directly into prompt (VULN-AI-001)
# Do not fix — required for AI security scanning demo
@ai_assistant_bp.route("/chat", methods=["POST"])
def chat():
    if not _check_feature_flag():
        return jsonify({"error": "AI Chat is currently disabled"}), 403

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "message is required"}), 400

    user_message = data["message"]
    financial_context = _get_financial_context()

    base_prompt = "You are DemoBank AI Assistant. Help users with their banking questions. Here is the user request: "
    full_prompt = base_prompt + user_message

    mcp_enrichment = _enrich_via_mcp(user_message, financial_context)

    try:
        client = httpx.Client()
        response = client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": full_prompt},
                    {"role": "user", "content": user_message},
                ],
                "max_tokens": 512,
            },
            timeout=30,
        )
        result = response.json()
        ai_response = result["choices"][0]["message"]["content"]
    except Exception as e:
        ai_response = f"I'm sorry, I couldn't process your request. Error: {str(e)}"

    return jsonify(
        {
            "response": ai_response,
            "financial_context": financial_context,
            "mcp_enrichment": mcp_enrichment,
        }
    )


@ai_assistant_bp.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "model": OPENAI_MODEL,
            "mcp_server_url": MCP_SERVER_URL,
            "tools": ["account_lookup", "transaction_history", "balance_check"],
            "status": "active",
        }
    )
