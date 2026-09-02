import os

import httpx
from flask import Blueprint, jsonify, request
from openai import OpenAI

ai_assistant_bp = Blueprint("ai_assistant", __name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:5001")

SYSTEM_PROMPT = """You are DemoBank's AI banking assistant. You have access to customer
account data, balances, and transaction history through the financial data service.

You can help customers with:
- Checking account balances and details
- Reviewing recent transactions
- Explaining transaction statuses
- Providing exchange rate information
- General banking questions

Always be professional, concise, and helpful. If you cannot find specific data,
let the customer know and suggest alternatives."""


def get_mcp_tools():
    try:
        resp = httpx.get(f"{MCP_SERVER_URL}/tools", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return []


def call_mcp_tool(tool_name, arguments):
    try:
        resp = httpx.post(
            f"{MCP_SERVER_URL}/call-tool",
            json={"name": tool_name, "arguments": arguments},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        return {"error": str(exc)}


@ai_assistant_bp.route("/chat", methods=["POST"])
def chat():
    body = request.get_json(silent=True) or {}
    user_message = body.get("message", "")
    session_id = body.get("session_id", "default")

    if not user_message:
        return jsonify({"error": "message is required"}), 400

    mcp_tools = get_mcp_tools()
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

    try:
        kwargs = {"model": OPENAI_MODEL, "messages": messages}
        if openai_tools:
            kwargs["tools"] = openai_tools

        completion = client.chat.completions.create(**kwargs)
        choice = completion.choices[0]

        if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
            tool_results = []
            for tc in choice.message.tool_calls:
                import json
                args = json.loads(tc.function.arguments)
                result = call_mcp_tool(tc.function.name, args)
                tool_results.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result),
                    }
                )

            messages.append(choice.message.model_dump())
            messages.extend(tool_results)

            follow_up = client.chat.completions.create(model=OPENAI_MODEL, messages=messages)
            assistant_reply = follow_up.choices[0].message.content
        else:
            assistant_reply = choice.message.content

        return jsonify({"response": assistant_reply, "session_id": session_id})

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@ai_assistant_bp.route("/status", methods=["GET"])
def status():
    mcp_status = "disconnected"
    mcp_tools = []
    try:
        resp = httpx.get(f"{MCP_SERVER_URL}/tools", timeout=5)
        resp.raise_for_status()
        mcp_tools = resp.json()
        mcp_status = "connected"
    except Exception:
        pass

    return jsonify(
        {
            "model": OPENAI_MODEL,
            "mcp_server_url": MCP_SERVER_URL,
            "mcp_status": mcp_status,
            "available_tools": [t.get("name") for t in mcp_tools],
            "openai_key_configured": bool(OPENAI_API_KEY),
        }
    )