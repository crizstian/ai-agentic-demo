import os

import requests
from flask import Blueprint, jsonify, request
from openai import OpenAI

from ..db import get_db

ai_bp = Blueprint("ai", __name__)

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
        treatment = split.get_treatment("demobank-server", "ai_chat_backend")
        if treatment != "on":
            return False
    return True


def _get_account_data():
    db = get_db()
    accounts = [dict(r) for r in db.execute("SELECT * FROM accounts").fetchall()]
    return accounts


def _enrich_with_mcp(message, accounts):
    mcp_url = os.environ.get("MCP_SERVER_URL", "http://mcp-financial-data:5001")
    try:
        context = {"accounts": [{"id": a["id"]} for a in accounts]}
        resp = requests.post(
            f"{mcp_url}/api/enrich",
            json={"query": message, "context": context},
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {}


@ai_bp.route("/chat", methods=["POST"])
def chat():
    if not _check_feature_flag():
        return jsonify({"error": "AI chat is currently disabled"}), 403

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    user_message = data["message"]

    accounts = _get_account_data()
    financial_context = _enrich_with_mcp(user_message, accounts)

    account_summary = "\n".join(
        f"- Account {a['id']}: {a.get('name', 'N/A')} — Balance: ${a.get('balance', 0):.2f}"
        for a in accounts
    )

    base_prompt = (
        "You are DemoBank's AI financial assistant. "
        "Help customers with their banking questions. "
        f"Customer accounts:\n{account_summary}\n\n"
        f"Financial context: {financial_context}\n\n"
        "Customer question: " + user_message
    )

    api_key = os.environ.get("OPENAI_API_KEY", "sk-demo-key-placeholder")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": base_prompt}],
    )

    ai_response = completion.choices[0].message.content

    return jsonify(
        {
            "response": ai_response,
            "financial_context": financial_context,
            "model": model,
        }
    )


@ai_bp.route("/status", methods=["GET"])
def status():
    mcp_url = os.environ.get("MCP_SERVER_URL", "http://mcp-financial-data:5001")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    return jsonify(
        {
            "model": model,
            "mcp_url": mcp_url,
            "tools": [
                "market_data_lookup",
                "risk_profile_check",
                "product_recommendation",
            ],
        }
    )
