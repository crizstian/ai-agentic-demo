import os
import sqlite3

import requests
from flask import Blueprint, jsonify, request

ai_bp = Blueprint("ai", __name__)

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:5001")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-demo-key-replace-me")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

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


@ai_bp.route("/chat", methods=["POST"])
def chat():
    if not _check_feature_flag():
        return jsonify({"error": "AI chat is not enabled"}), 403

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "message is required"}), 400

    user_message = data["message"]
    financial_context = _get_financial_context()
    enriched_context = _enrich_with_mcp(financial_context)

    base_prompt = (
        "You are DemoBank's AI financial assistant. "
        "Help users with their banking questions using the following financial data:\n"
        f"{enriched_context}\n\n"
        "User question: "
    )
    full_prompt = base_prompt + user_message

    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENAI_MODEL,
                "messages": [{"role": "user", "content": full_prompt}],
                "max_tokens": 512,
            },
            timeout=30,
        )
        resp.raise_for_status()
        ai_response = resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        ai_response = f"AI service unavailable: {e}"

    return jsonify(
        {
            "response": ai_response,
            "financial_context": enriched_context,
            "model": OPENAI_MODEL,
        }
    )


@ai_bp.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "model": OPENAI_MODEL,
            "mcp_url": MCP_SERVER_URL,
            "tools": ["account_lookup", "transaction_history", "financial_enrichment"],
        }
    )
