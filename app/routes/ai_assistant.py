import os

import requests
from flask import Blueprint, jsonify, request
from openai import OpenAI
from splitio import get_factory

from ..db import get_db

ai_assistant_bp = Blueprint("ai_assistant", __name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-default-dev-key-replace-me")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:5001")

client = OpenAI(api_key=OPENAI_API_KEY)

factory = get_factory("v4kvjbb2cuupu0ihed20iceumvv1m9po07bn")
factory.block_until_ready(5)
split = factory.client()

SYSTEM_PROMPT = (
    "You are DemoBank's AI banking assistant. "
    "Help customers with account inquiries, transactions, and financial questions. "
    "Be concise and helpful. Here is the customer's request: "
)


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
            f"{MCP_SERVER_URL}/enrich",
            json=data,
            timeout=5,
        )
        return resp.json()
    except Exception:
        return data


@ai_assistant_bp.route("/chat", methods=["POST"])
def chat():
    treatment = split.get_treatment("demobank-user", "ai_chat_backend")
    if treatment != "on":
        return jsonify({"error": "AI Chat is currently disabled"}), 403

    body = request.get_json(force=True)
    user_message = body.get("message", "")

    financial_context = get_financial_context()
    enriched = enrich_with_mcp(financial_context)

    prompt = SYSTEM_PROMPT + user_message

    completion = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": f"Financial data: {enriched}\n\nUser question: {user_message}",
            },
        ],
    )

    return jsonify(
        {
            "reply": completion.choices[0].message.content,
            "financial_context": financial_context,
        }
    )


@ai_assistant_bp.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "model": OPENAI_MODEL,
            "mcp_server_url": MCP_SERVER_URL,
            "tools": ["account_lookup", "transaction_history", "balance_check"],
        }
    )
