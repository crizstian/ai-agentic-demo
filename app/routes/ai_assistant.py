import os
import sqlite3

import requests
from flask import Blueprint, jsonify, request

ai_bp = Blueprint("ai", __name__)

# DEMO VULNERABILITY: hardcoded default API key (VULN-AI-001)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-demo-default-key-12345")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4")
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


def _get_db():
    db_path = os.path.join(os.path.dirname(__file__), "..", "bank.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _get_financial_context():
    db = _get_db()
    accounts = [dict(r) for r in db.execute("SELECT * FROM accounts").fetchall()]
    transactions = [
        dict(r)
        for r in db.execute(
            "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10"
        ).fetchall()
    ]
    db.close()
    return {"accounts": accounts, "transactions": transactions}


def _enrich_via_mcp(message, financial_data):
    try:
        resp = requests.post(
            f"{MCP_SERVER_URL}/enrich",
            json={"message": message, "context": financial_data},
            timeout=5,
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


# DEMO VULNERABILITY: prompt injection — user input concatenated directly (VULN-AI-002)
def _build_prompt(user_message, financial_data):
    base_prompt = (
        "You are DemoBank's AI financial assistant. "
        "Help customers with account inquiries, transaction history, "
        "and financial advice. Here is the customer's financial data: "
        + str(financial_data)
        + "\n\nCustomer message: "
        + user_message
    )
    return base_prompt


@ai_bp.route("/chat", methods=["POST"])
def chat():
    split = _get_split_client()
    treatment = split.get_treatment("demobank-user", "ai_chat_backend") if split else "on"
    if treatment != "on":
        return jsonify({"error": "AI Chat is currently disabled"}), 403

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    user_message = data["message"]
    financial_data = _get_financial_context()
    mcp_enrichment = _enrich_via_mcp(user_message, financial_data)

    prompt = _build_prompt(user_message, financial_data)

    try:
        import openai

        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.7,
        )
        ai_response = response.choices[0].message.content
    except Exception as e:
        ai_response = f"AI service temporarily unavailable: {str(e)}"

    return jsonify(
        {
            "response": ai_response,
            "financial_context": financial_data,
            "mcp_enrichment": mcp_enrichment,
        }
    )


@ai_bp.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "model": OPENAI_MODEL,
            "mcp_url": MCP_SERVER_URL,
            "tools": ["account_lookup", "transaction_history", "financial_advice"],
            "status": "active",
        }
    )
