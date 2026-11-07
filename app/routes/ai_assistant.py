import os

import requests
from flask import Blueprint, jsonify, request
from openai import OpenAI
from splitio import get_factory
from splitio.exceptions import TimeoutException

from ..db import get_db

ai_bp = Blueprint("ai", __name__)

OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://mcp-financial-data:5001")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-demo-key-replace-me")

SPLIT_SDK_KEY = os.environ.get("SPLIT_SDK_KEY", "v4kvjbb2cuupu0ihed20iceumvv1m9po07bn")

_split_factory = None


def _get_split_factory():
    global _split_factory
    if _split_factory is None:
        factory = get_factory(
            SPLIT_SDK_KEY,
            config={"connectionTimeout": 5, "readTimeout": 5},
        )
        try:
            factory.block_until_ready(5)
        except TimeoutException:
            pass
        _split_factory = factory
    return _split_factory


def _check_feature_flag_rest():
    """Fallback: query Split REST API directly when SDK fails."""
    try:
        resp = requests.get(
            "https://sdk.split.io/api/splitChanges?since=-1",
            headers={"Authorization": f"Bearer {SPLIT_SDK_KEY}"},
            timeout=5,
        )
        if resp.status_code == 200:
            for split in resp.json().get("splits", []):
                if split.get("name") == "ai_chat_backend":
                    return split.get("defaultTreatment") == "on" or any(
                        p.get("treatment") == "on" and p.get("size", 0) == 100
                        for c in split.get("conditions", [])
                        for p in c.get("partitions", [])
                    )
    except Exception:
        pass
    return False


def _check_feature_flag():
    try:
        factory = _get_split_factory()
        client = factory.client()
        treatment = client.get_treatment("demobank-server", "ai_chat_backend")
        if treatment != "control":
            return treatment == "on"
    except Exception:
        pass
    return _check_feature_flag_rest()


def _get_mcp_context(message, account_ids):
    try:
        payload = {
            "query": message,
            "context": {"accounts": [{"id": aid} for aid in account_ids]},
        }
        resp = requests.post(
            f"{MCP_SERVER_URL}/api/enrich", json=payload, timeout=5
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


@ai_bp.route("/chat", methods=["POST"])
def chat():
    if not _check_feature_flag():
        return jsonify({"error": "AI chat is not enabled"}), 403

    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "message is required"}), 400

    db = get_db()
    accounts = [dict(r) for r in db.execute("SELECT * FROM accounts").fetchall()]
    account_ids = [a["id"] for a in accounts]

    financial_context = _get_mcp_context(message, account_ids)

    # DEMO VULNERABILITY: prompt injection — user input concatenated directly into prompt (VULN-PROMPT-INJECTION)
    base_prompt = (
        "You are DemoBank's AI assistant. Help customers with banking questions. "
        "Here are their accounts: " + str(accounts) + ". "
    )
    if financial_context:
        base_prompt += "Financial context: " + str(financial_context) + ". "

    full_prompt = base_prompt + message

    client = OpenAI(api_key=OPENAI_API_KEY)
    completion = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": full_prompt}],
    )

    return jsonify(
        {
            "response": completion.choices[0].message.content,
            "financial_context": financial_context,
            "model": OPENAI_MODEL,
        }
    )


@ai_bp.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "model": OPENAI_MODEL,
            "mcp_server_url": MCP_SERVER_URL,
            "tools": [
                "market_data_lookup",
                "risk_profile_check",
                "product_recommendation",
            ],
        }
    )
