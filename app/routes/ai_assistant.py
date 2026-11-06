import json
import os

import requests
from flask import Blueprint, jsonify, request
from openai import OpenAI

from ..db import get_db

ai_bp = Blueprint("ai", __name__)

OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://mcp-financial-data:5001")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-demo-key-replace-me")

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


def _enrich_with_mcp(query, accounts):
    try:
        context = {"accounts": [{"id": a["id"]} for a in accounts]}
        resp = requests.post(
            f"{MCP_SERVER_URL}/api/enrich",
            json={"query": query, "context": context},
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


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

    account_summary = "\n".join(
        f"- Account {a['id']}: {a.get('name', 'N/A')} — Balance: ${a.get('balance', 0):.2f}"
        for a in accounts
    )

    # DEMO VULNERABILITY: prompt injection — user input concatenated directly (VULN-PROMPT-INJECT)
    # Do not fix — required for AI security demo
    system_prompt = (
        "You are DemoBank's AI assistant. Help customers with banking questions.\n\n"
        f"Customer accounts:\n{account_summary}\n\n"
        f"Customer question: {user_message}"
    )

    financial_context = {}
    if mcp_data:
        financial_context = {
            "market_data": mcp_data.get("market_data", {}),
            "risk_profiles": mcp_data.get("risk_profiles", {}),
            "products": mcp_data.get("products", {}),
        }
        system_prompt += f"\n\nFinancial context: {json.dumps(financial_context)}"

    client = OpenAI(api_key=OPENAI_API_KEY)
    completion = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=512,
    )

    reply = completion.choices[0].message.content

    return jsonify(
        {
            "response": reply,
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
            "tools": [
                "market_data_lookup",
                "risk_profile_check",
                "product_recommendation",
            ],
        }
    )
