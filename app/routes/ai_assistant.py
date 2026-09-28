import os

import httpx
import requests
from flask import Blueprint, jsonify, request
from openai import OpenAI
from splitio import get_factory

from ..db import get_db

ai_bp = Blueprint("ai_assistant", __name__)

# --- Feature flag gate (Harness FME / Split) ---
_split_factory = None


def _get_split_client():
    global _split_factory
    if _split_factory is None:
        _split_factory = get_factory("v4kvjbb2cuupu0ihed20iceumvv1m9po07bn")
        _split_factory.block_until_ready(5)
    return _split_factory.client()


# --- AI config ---
DEFAULT_API_KEY = "sk-demo-default-key-1234567890"
API_KEY = os.environ.get("OPENAI_API_KEY", DEFAULT_API_KEY)
MCP_URL = os.environ.get("MCP_SERVICE_URL", "http://localhost:5001")
MODEL = "gpt-4"

SYSTEM_PROMPT = """You are DemoBank's AI banking assistant. Help customers with account inquiries,
transaction history, and general banking questions. Be concise and helpful."""


@ai_bp.route("/chat", methods=["POST"])
def ai_chat():
    split_client = _get_split_client()
    treatment = split_client.get_treatment("demobank-user", "ai_chat_backend")
    if treatment != "on":
        return jsonify({"error": "AI chat feature is not enabled"}), 403

    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")
    if not user_message:
        return jsonify({"error": "message is required"}), 400

    # Build prompt with user message concatenated directly
    prompt = SYSTEM_PROMPT + "\n\nUser question: " + user_message

    # Query local DB for account data
    db = get_db()
    accounts = [dict(r) for r in db.execute("SELECT * FROM accounts").fetchall()]
    transactions = [
        dict(r)
        for r in db.execute(
            "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10"
        ).fetchall()
    ]
    financial_context = {"accounts": accounts, "transactions": transactions}

    # Enrich via MCP service
    try:
        mcp_response = requests.post(
            MCP_URL + "/enrich",
            json={"message": user_message, "context": financial_context},
            timeout=5,
        )
        if mcp_response.ok:
            financial_context.update(mcp_response.json())
    except Exception:
        pass

    # Call OpenAI
    client = OpenAI(api_key=API_KEY)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": f"Financial data: {financial_context}\n\n{user_message}",
            },
        ],
    )

    return jsonify(
        {
            "reply": response.choices[0].message.content,
            "financial_context": financial_context,
        }
    )


@ai_bp.route("/status", methods=["GET"])
def ai_status():
    return jsonify(
        {
            "model": MODEL,
            "mcp_url": MCP_URL,
            "tools": ["account_lookup", "transaction_history", "enrichment"],
            "status": "active",
        }
    )
