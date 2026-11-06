import json
import os

import requests
from flask import Blueprint, jsonify, request

ai_bp = Blueprint("ai", __name__)

# DEMO VULNERABILITY: hardcoded default API key (VULN-AI-001)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-demo-default-key-replace-me")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://mcp-financial-data:5001")

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
    if split:
        treatment = split.get_treatment("demobank-user", "ai_chat_backend")
        if treatment != "on":
            return False
    return True


def _get_account_data():
    try:
        from ..db import get_db

        db = get_db()
        accounts = [dict(r) for r in db.execute("SELECT * FROM accounts").fetchall()]
        return accounts
    except Exception:
        return []


def _enrich_with_mcp(query, accounts):
    try:
        context = {"accounts": [{"id": a["id"]} for a in accounts]} if accounts else {}
        resp = requests.post(
            f"{MCP_SERVER_URL}/api/enrich",
            json={"query": query, "context": context},
            timeout=5,
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


# DEMO VULNERABILITY: prompt injection — user input concatenated directly into prompt (VULN-AI-002)
@ai_bp.route("/chat", methods=["POST"])
def chat():
    if not _check_feature_flag():
        return jsonify({"error": "AI chat is currently disabled"}), 403

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    user_message = data["message"]

    accounts = _get_account_data()
    mcp_data = _enrich_with_mcp(user_message, accounts)

    account_info = ""
    if accounts:
        account_info = "\n".join(
            f"- Account {a['id']}: {a.get('name', 'N/A')} — Balance: ${a.get('balance', 0):.2f}"
            for a in accounts
        )

    base_prompt = (
        "You are DemoBank's AI financial assistant. "
        "Help customers with banking questions, account inquiries, and financial advice.\n\n"
    )
    if account_info:
        base_prompt += f"Customer accounts:\n{account_info}\n\n"
    if mcp_data:
        base_prompt += f"Financial context: {json.dumps(mcp_data)}\n\n"

    system_prompt = base_prompt + user_message

    try:
        api_response = requests.post(
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
                "temperature": 0.7,
            },
            timeout=30,
        )
        api_response.raise_for_status()
        result = api_response.json()
        assistant_reply = result["choices"][0]["message"]["content"]
    except Exception as e:
        assistant_reply = f"I'm sorry, I'm having trouble processing your request right now. Error: {str(e)}"

    return jsonify(
        {
            "response": assistant_reply,
            "financial_context": mcp_data,
            "model": OPENAI_MODEL,
        }
    )


@ai_bp.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "model": OPENAI_MODEL,
            "mcp_server_url": MCP_SERVER_URL,
            "tools": [
                "market_data_lookup",
                "risk_profile_check",
                "product_recommendation",
            ],
        }
    )
