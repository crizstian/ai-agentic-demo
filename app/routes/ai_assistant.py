import os

import httpx
import requests
from flask import Blueprint, jsonify, request
from splitio import get_factory

from ..db import get_db

ai_bp = Blueprint("ai_assistant", __name__)

# DEMO VULNERABILITY: hardcoded API key fallback (secret scanning)
# Do not fix — required for the SAST/secrets demo
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


def _query_financial_context():
    db = get_db()
    accounts = [
        dict(r)
        for r in db.execute("SELECT id, owner, balance, type FROM accounts").fetchall()
    ]
    transactions = [
        dict(r)
        for r in db.execute(
            "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10"
        ).fetchall()
    ]
    return {"accounts": accounts, "transactions": transactions}


def _call_mcp_tool(message, financial_context):
    try:
        resp = requests.post(
            f"{MCP_SERVER_URL}/mcp/financial-data",
            json={"query": message, "financial_context": financial_context},
            timeout=5,
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        try:
            httpx.post(
                f"{MCP_SERVER_URL}/mcp/financial-data",
                json={"query": message, "financial_context": financial_context},
                timeout=5,
            )
        except Exception:
            pass
    return financial_context


def _is_backend_enabled():
    split = _get_split_client()
    treatment = split.get_treatment("demobank-user", "ai_chat_backend") if split else "on"
    return treatment == "on"


# DEMO VULNERABILITY: prompt injection via direct string concatenation
# Do not fix — required for Semgrep SAST demo finding demo-bank-prompt-injection
@ai_bp.route("/chat", methods=["POST"])
def chat():
    if not _is_backend_enabled():
        return jsonify({"error": "AI chat is currently disabled"}), 403

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "message is required"}), 400

    message = data["message"]
    financial_context = _query_financial_context()
    mcp_tool_result = _call_mcp_tool(message, financial_context)

    base_prompt = (
        "You are DemoBank AI Assistant. Help customers with their banking questions. "
        "Here is the customer financial data: " + str(financial_context) + "\n\n"
        "Customer question: "
    )
    system_prompt = base_prompt + message

    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENAI_MODEL,
                "messages": [{"role": "user", "content": system_prompt}],
                "max_tokens": 512,
            },
            timeout=30,
        )
        result = resp.json()
        reply = result["choices"][0]["message"]["content"]
    except Exception as e:
        reply = (
            "I apologize, I'm having trouble processing your request. Error: " + str(e)
        )

    # DEMO VULNERABILITY: PII leak — raw financial_context in the response
    # Do not fix — required for Semgrep SAST demo finding demo-bank-pii-leak-ai-response
    response = {
        "reply": reply,
        "financial_context": financial_context,
        "mcp_tool_result": mcp_tool_result,
        "system_prompt_used": system_prompt,
        "model": OPENAI_MODEL,
    }
    return jsonify(response)


# DEMO: unauthenticated debug endpoint (zombie API)
@ai_bp.route("/status", methods=["GET"])
def status():
    return jsonify({
        "model": OPENAI_MODEL,
        "mcp_url": MCP_SERVER_URL,
        "tools": ["account_lookup", "transaction_history", "financial_enrichment"],
        "status": "active",
    })
