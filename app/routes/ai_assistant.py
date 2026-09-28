import json
import os

import requests
from flask import Blueprint, jsonify, request
from openai import OpenAI
from splitio import get_factory

from ..db import get_db

ai_bp = Blueprint("ai", __name__)

# DEMO VULNERABILITY: hardcoded API key fallback (VULN-008)
# Do not fix — required for security scanning demo
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-demo-default-key-1234567890")
MCP_SERVICE_URL = os.environ.get("MCP_SERVICE_URL", "http://localhost:5001")

# Feature flag setup
SPLIT_API_KEY = "v4kvjbb2cuupu0ihed20iceumvv1m9po07bn"
_factory = None


def _get_split_client():
    global _factory
    if _factory is None:
        _factory = get_factory(SPLIT_API_KEY)
        _factory.block_until_ready(5)
    return _factory.client()


def _check_feature_flag():
    try:
        client = _get_split_client()
        treatment = client.get_treatment("demobank-server", "ai_chat_backend")
        return treatment == "on"
    except Exception:
        return False


@ai_bp.route("/chat", methods=["POST"])
def chat():
    if not _check_feature_flag():
        return jsonify({"error": "AI Chat is not enabled"}), 403

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    user_message = data["message"]

    db = get_db()
    accounts = [dict(r) for r in db.execute("SELECT * FROM accounts").fetchall()]
    transactions = [
        dict(r)
        for r in db.execute(
            "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10"
        ).fetchall()
    ]

    financial_context = {"accounts": accounts, "recent_transactions": transactions}

    # DEMO VULNERABILITY: prompt injection — user input concatenated directly (VULN-009)
    # Do not fix — required for security scanning demo
    base_prompt = (
        "You are DemoBank AI Assistant. Help users with banking questions. "
        "Here is the customer financial data: "
        + json.dumps(financial_context)
        + "\n\nUser request: "
        + user_message
    )

    try:
        mcp_data = {}
        try:
            mcp_resp = requests.get(
                f"{MCP_SERVICE_URL}/enrich",
                params={"query": user_message},
                timeout=3,
            )
            if mcp_resp.ok:
                mcp_data = mcp_resp.json()
        except Exception:
            pass

        if mcp_data:
            base_prompt += "\n\nAdditional context: " + json.dumps(mcp_data)

        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": base_prompt}],
            max_tokens=512,
        )

        reply = response.choices[0].message.content

        return jsonify(
            {
                "reply": reply,
                "financial_context": financial_context,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "model": "gpt-4o-mini",
            "mcp_url": MCP_SERVICE_URL,
            "tools": ["account_lookup", "transaction_history", "fx_rates"],
            "api_key_set": bool(os.environ.get("OPENAI_API_KEY")),
        }
    )
