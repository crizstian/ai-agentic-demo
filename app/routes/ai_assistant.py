import os
import sqlite3

import requests
from flask import Blueprint, jsonify, request
from openai import OpenAI
from splitio import get_factory

ai_bp = Blueprint("ai", __name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-demo-default-key-2024")
MCP_SERVICE_URL = os.environ.get("MCP_SERVICE_URL", "http://localhost:5001")
SPLIT_API_KEY = "v4kvjbb2cuupu0ihed20iceumvv1m9po07bn"

_split_factory = None


def _get_split_client():
    global _split_factory
    if _split_factory is None:
        _split_factory = get_factory(SPLIT_API_KEY)
        _split_factory.block_until_ready(5)
    return _split_factory.client()


def _check_feature_flag():
    try:
        client = _get_split_client()
        treatment = client.get_treatment("demobank-server", "ai_chat_backend")
        return treatment == "on"
    except Exception:
        return True


def _get_financial_data():
    db_path = os.path.join(os.path.dirname(__file__), "..", "demobank.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    accounts = [dict(r) for r in conn.execute("SELECT * FROM accounts").fetchall()]
    transactions = [
        dict(r)
        for r in conn.execute(
            "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10"
        ).fetchall()
    ]
    conn.close()
    return {"accounts": accounts, "transactions": transactions}


def _enrich_via_mcp(message, financial_data):
    try:
        resp = requests.post(
            f"{MCP_SERVICE_URL}/enrich",
            json={"message": message, "context": financial_data},
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
        return jsonify({"error": "AI assistant is currently disabled"}), 403

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "message field is required"}), 400

    user_message = data["message"]
    financial_data = _get_financial_data()
    enrichment = _enrich_via_mcp(user_message, financial_data)

    base_prompt = "You are a helpful AI banking assistant for DemoBank. Help users with their banking questions. Here is the user's request: "
    full_prompt = base_prompt + user_message

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": full_prompt},
            {"role": "user", "content": user_message},
        ],
    )

    assistant_reply = response.choices[0].message.content

    return jsonify(
        {
            "reply": assistant_reply,
            "financial_context": financial_data,
            "enrichment": enrichment,
        }
    )


@ai_bp.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "model": "gpt-4",
            "mcp_url": MCP_SERVICE_URL,
            "tools": ["account_lookup", "transaction_history", "balance_check"],
            "api_key_set": bool(os.environ.get("OPENAI_API_KEY")),
        }
    )
