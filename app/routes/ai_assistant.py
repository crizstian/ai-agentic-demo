import os
from urllib.parse import urlparse

import httpx
from flask import Blueprint, jsonify, request
from openai import OpenAI

from splitio import get_factory

ai_bp = Blueprint("ai", __name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
_raw_mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:5001")
_parsed = urlparse(_raw_mcp_url)
if _parsed.scheme not in ("http", "https"):
    raise ValueError(f"MCP_SERVER_URL must use http or https scheme, got: {_parsed.scheme}")
MCP_SERVER_URL = _raw_mcp_url
AI_MODEL = os.getenv("AI_MODEL", "gpt-4")

SYSTEM_PROMPT = (
    "You are DemoBank's AI banking assistant. You have access to customer "
    "account data, balances, and transaction history through the connected "
    "financial data service. Help customers check balances, review "
    "transactions, understand exchange rates, and answer general banking "
    "questions. Be concise, professional, and helpful."
)

# --- Split.io singleton ---
SPLITIO_SERVER_KEY = os.getenv("SPLITIO_SERVER_KEY", "")
_split_factory = get_factory(SPLITIO_SERVER_KEY)
_split_factory.block_until_ready(5)
_split_client = _split_factory.client()


def _get_mcp_tools():
    try:
        resp = httpx.get(f"{MCP_SERVER_URL}/tools", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return []


def _call_mcp_tool(tool_name, arguments):
    try:
        resp = httpx.post(
            f"{MCP_SERVER_URL}/call-tool",
            json={"name": tool_name, "arguments": arguments},
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


@ai_bp.route("/chat", methods=["POST"])
def chat():
    treatment = _split_client.get_treatment("demobank-user", "ai_chat_backend")
    if treatment != "on":
        return jsonify(
            {"error": "AI Chat is currently disabled", "status": "disabled"}
        ), 403

    body = request.get_json(silent=True) or {}
    user_message = body.get("message", "")
    session_id = body.get("session_id", "default")

    if not user_message:
        return jsonify({"error": "message is required"}), 400

    mcp_tools = _get_mcp_tools()
    openai_tools = []
    for tool in mcp_tools:
        openai_tools.append(
            {
                "type": "function",
                "function": {
                    "name": tool.get("name"),
                    "description": tool.get("description", ""),
                    "parameters": tool.get("inputSchema", {"type": "object", "properties": {}}),
                },
            }
        )

    client = OpenAI(api_key=OPENAI_API_KEY)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    kwargs = {"model": AI_MODEL, "messages": messages}
    if openai_tools:
        kwargs["tools"] = openai_tools

    completion = client.chat.completions.create(**kwargs)
    assistant_msg = completion.choices[0].message

    if assistant_msg.tool_calls:
        messages.append(assistant_msg)
        for tc in assistant_msg.tool_calls:
            import json

            args = json.loads(tc.function.arguments) if tc.function.arguments else {}
            result = _call_mcp_tool(tc.function.name, args)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result) if result else "Tool call failed",
                }
            )
        follow_up = client.chat.completions.create(model=AI_MODEL, messages=messages)
        assistant_msg = follow_up.choices[0].message

    return jsonify({"response": assistant_msg.content})


@ai_bp.route("/status", methods=["GET"])
def status():
    mcp_connected = False
    mcp_tools = []
    try:
        resp = httpx.get(f"{MCP_SERVER_URL}/tools", timeout=5)
        if resp.status_code == 200:
            mcp_connected = True
            mcp_tools = [t.get("name") for t in resp.json()]
    except Exception:
        pass

    return jsonify(
        {
            "model": AI_MODEL,
            "mcp_server_url": MCP_SERVER_URL,
            "mcp_connected": mcp_connected,
            "mcp_tools": mcp_tools,
            "openai_key_set": bool(OPENAI_API_KEY),
        }
    )


@ai_bp.route("/ff/ai-chat", methods=["GET"])
def ff_status():
    treatment = _split_client.get_treatment("demobank-user", "ai_chat_backend")
    return jsonify({"flag": "ai_chat_backend", "treatment": treatment})
