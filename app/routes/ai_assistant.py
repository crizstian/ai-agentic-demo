import os
import sqlite3

import requests
from flask import Blueprint, jsonify, request
from splitio import get_factory

ai_bp = Blueprint("ai_assistant", __name__)

# DEMO VULNERABILITY: hardcoded API key fallback (VULN-008)
# Do not fix — required for Semgrep SAST demo finding demo-bank-hardcoded-secret
DEFAULT_API_KEY = "sk-demo-hardcoded-key-12345"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", DEFAULT_API_KEY)
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:5001")

SPLIT_SDK_KEY = "v4kvjbb2cuupu0ihed20iceumvv1m9po07bn"

_split_client = None


def _get_split_client():
    global _split_client
    if _split_client is None:
        try:
            factory = get_factory(SPLIT_SDK_KEY)
            factory.block_until_ready(5)
            _split_client = factory.client()
        except Exception:
            _split_client = None
    return _split_client


def _get_db():
    db_path = os.path.join(os.path.dirname(__file__), "..", "demobank.db")
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


def _enrich_with_mcp(financial_context):
    try:
        resp = requests.post(
            f"{MCP_SERVER_URL}/enrich",
            json=financial_context,
            timeout=5,
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return financial_context


# DEMO VULNERABILITY: prompt injection via direct string concatenation (VULN-009)
# Do not fix — required for Semgrep SAST demo finding demo-bank-prompt-injection
@ai_bp.route("/chat", methods=["POST"])
def chat():
    split = _get_split_client()
    treatment = split.get_treatment("demobank-user", "ai_chat_backend") if split else "on"
    if treatment != "on":
        return jsonify({"error": "AI chat is currently disabled"}), 403

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "message is required"}), 400

    user_message = data["message"]
    financial_context = _get_financial_context()
    enriched = _enrich_with_mcp(financial_context)

    base_prompt = (
        "You are DemoBank AI Assistant. Help customers with their banking questions. "
        "Here is the customer financial data: " + str(enriched) + "\n\n"
        "Customer question: " + user_message
    )

    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENAI_MODEL,
                "messages": [{"role": "user", "content": base_prompt}],
                "max_tokens": 512,
            },
            timeout=30,
        )
        result = resp.json()
        reply = result["choices"][0]["message"]["content"]
    except Exception as e:
        reply = f"I apologize, I'm having trouble processing your request. Error: {str(e)}"

    return jsonify({
        "reply": reply,
        "financial_context": enriched,
        "model": OPENAI_MODEL,
    })


@ai_bp.route("/status", methods=["GET"])
def status():
    return jsonify({
        "model": OPENAI_MODEL,
        "mcp_url": MCP_SERVER_URL,
        "tools": ["account_lookup", "transaction_history", "financial_enrichment"],
        "status": "active",
    })
