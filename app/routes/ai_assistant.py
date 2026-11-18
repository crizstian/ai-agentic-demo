import json
import os

import httpx
import requests
import urllib3
from flask import Blueprint, jsonify, request
from openai import OpenAI
from splitio import get_factory
from splitio.exceptions import TimeoutException

from ..db import get_db

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ai_bp = Blueprint("ai", __name__)

OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://mcp-financial-data:5001")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-demo-key-replace-me")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", None)
SELF_URL = os.environ.get("SELF_URL", "https://demobank-e2e.selatam.harness-demo.site")
FF_OVERRIDE = os.environ.get("AI_CHAT_ENABLED", None)

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
    if FF_OVERRIDE is not None:
        return FF_OVERRIDE.lower() in ("1", "true", "on")
    try:
        factory = _get_split_factory()
        client = factory.client()
        treatment = client.get_treatment("demobank-server", "ai_chat_backend")
        if treatment != "control":
            return treatment == "on"
    except Exception:
        pass
    return _check_feature_flag_rest()


def _execute_tool_call(tool_call):
    """Execute an agent tool call by routing through nginx (SELF_URL) for Traceable visibility."""
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    if name == "get_account":
        url = f"{SELF_URL}/api/accounts/{args['account_id']}"
    elif name == "list_accounts":
        url = f"{SELF_URL}/api/accounts"
    else:
        return json.dumps({"error": f"Unknown tool: {name}"})

    headers = {
        "User-Agent": "DemoBank-AI-Agent/1.0 (OpenAI-Function-Call)",
        "X-AI-Agent": "true",
        "X-AI-Agent-Tool": name,
        "X-AI-Agent-Model": OPENAI_MODEL,
    }
    print(f"[AI-AGENT] Tool call: {name}({args}) -> {url}")
    try:
        resp = requests.get(url, headers=headers, verify=False, timeout=10)
        return resp.text
    except Exception as e:
        return json.dumps({"error": str(e)})


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


LLM_INTERNAL_URL = OPENAI_BASE_URL or "http://mock-openai:5002/v1"


@ai_bp.route("/llm/v1/chat/completions", methods=["POST"])
def llm_proxy():
    """Proxy LLM calls to mock-openai — routed through nginx so Traceable sees AI interactions."""
    body = request.get_json(silent=True) or {}
    try:
        resp = requests.post(
            f"{LLM_INTERNAL_URL}/chat/completions",
            json=body,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 502


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

    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=f"{SELF_URL}/api/ai/llm/v1",
        http_client=httpx.Client(verify=False),
    )

    messages = [{"role": "user", "content": full_prompt}]
    completion = client.chat.completions.create(model=OPENAI_MODEL, messages=messages)
    assistant_message = completion.choices[0].message
    agent_actions = 0

    agent_tools_log = []

    if assistant_message.tool_calls:
        agent_actions = len(assistant_message.tool_calls)
        print(f"[AI-AGENT] Received {agent_actions} tool_calls — executing through nginx")

        tool_results = []
        for tc in assistant_message.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments)
            agent_tools_log.append({"tool": name, "args": args})
            result = _execute_tool_call(tc)
            tool_results.append({"role": "tool", "tool_call_id": tc.id, "content": result})

        followup_messages = messages + [
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {"id": tc.id, "type": tc.type, "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in assistant_message.tool_calls
                ],
            },
            *tool_results,
        ]
        completion = client.chat.completions.create(model=OPENAI_MODEL, messages=followup_messages)
        assistant_message = completion.choices[0].message

    return jsonify(
        {
            "response": assistant_message.content,
            "financial_context": financial_context,
            "model": OPENAI_MODEL,
            "agent_actions": agent_actions,
            "agent_tools": agent_tools_log,
        }
    )


@ai_bp.route("/reset", methods=["POST"])
def reset_agent():
    """Reset the rogue agent conversation back to step 0."""
    try:
        base = OPENAI_BASE_URL or "http://mock-openai:5002/v1"
        reset_url = base.rstrip("/").rsplit("/v1", 1)[0] + "/v1/reset"
        resp = requests.post(reset_url, timeout=5)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
