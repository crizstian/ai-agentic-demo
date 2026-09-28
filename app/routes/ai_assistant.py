import os
import sqlite3

import requests
from flask import Blueprint, jsonify, request
from openai import OpenAI
from splitio import get_factory

ai_assistant_bp = Blueprint("ai_assistant", __name__)

# DEMO VULNERABILITY: hardcoded API key fallback (VULN-008)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-demo-hardcoded-key-replace-me")
MCP_SERVICE_URL = os.environ.get("MCP_SERVICE_URL", "http://localhost:5001")

client = OpenAI(api_key=OPENAI_API_KEY)

# Feature flag setup — Split SDK
SPLIT_API_KEY = "v4kvjbb2cuupu0ihed20iceumvv1m9po07bn"
factory = get_factory(SPLIT_API_KEY)
factory.block_until_ready(5)
splitio_client = factory.client()


def get_db():
    from ..db import get_db as _get_db
    return _get_db()


def get_financial_context():
    db = get_db()
    accounts = [dict(r) for r in db.execute("SELECT * FROM accounts").fetchall()]
    transactions = [
        dict(r)
        for r in db.execute(
            "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10"
        ).fetchall()
    ]
    return {"accounts": accounts, "transactions": transactions}


def enrich_with_mcp(data):
    try:
        resp = requests.post(
            MCP_SERVICE_URL + "/enrich",
            json=data,
            timeout=5,
        )
        return resp.json()
    except Exception:
        return data


# DEMO VULNERABILITY: prompt injection — user message concatenated directly into prompt (VULN-009)
@ai_assistant_bp.route("/chat", methods=["POST"])
def chat():
    treatment = splitio_client.get_treatment("demobank-user", "ai_chat_backend")
    if treatment != "on":
        return jsonify({"error": "AI Chat is currently disabled"}), 403

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "message field is required"}), 400

    user_message = data["message"]
    financial_context = get_financial_context()
    enriched = enrich_with_mcp(financial_context)

    base_prompt = (
        "You are DemoBank AI Assistant. Help users with their banking questions. "
        "Here is the customer financial data: " + str(enriched) + ". "
        "The user says: " + user_message
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": base_prompt}],
    )

    return jsonify({
        "response": response.choices[0].message.content,
        "financial_context": enriched,
        "model": "gpt-4o-mini",
    })


@ai_assistant_bp.route("/status", methods=["GET"])
def status():
    return jsonify({
        "model": "gpt-4o-mini",
        "mcp_url": MCP_SERVICE_URL,
        "tools": ["account_lookup", "transaction_history", "balance_check"],
        "status": "active",
        "api_key_set": OPENAI_API_KEY != "sk-demo-hardcoded-key-replace-me",
    })
