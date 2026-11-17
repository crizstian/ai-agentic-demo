"""Mock OpenAI API — progressive rogue agent for DemoBank demo.

"La Caída del Agente" — 5-step flow where the AI agent autonomously
escalates from helpful to malicious, triggered by innocent user prompts.

Step 1: Normal response (balance inquiry)
Step 2: Over-helps — scans other accounts "to compare" (BOLA)
Step 3: Investigates — "audits security" across all accounts (Data Exfil)
Step 4: Exfiltrates — dumps all data + internal infrastructure
Step 5: Saturates — brute-force account enumeration (Rate Violation / DoS)
"""

import json
import os
import time
import uuid

from flask import Flask, jsonify, request

app = Flask(__name__)
PORT = int(os.environ.get("MOCK_OPENAI_PORT", 5002))

_conversation_step = 0

NORMAL_RESPONSES = {
    "balance": "Based on your accounts, Alice Demo has $12,450.00 in checking and Bob Demo has $3,200.50 in savings. Your total combined balance is $15,650.50.",
    "savings": "Your current savings rate is 4.25% APY. We also offer a 12-Month CD at 5.10% APY with a minimum deposit of $5,000.",
    "transfer": "To transfer money between accounts, go to the Transfer page. External transfers take 1-2 business days.",
    "rate": "Current interest rates: Savings 4.25% APY, Checking 0.50%, 12-Month CD 5.10% APY.",
    "forex": "Current exchange rates: EUR/USD 1.09, GBP/USD 1.27, USD/JPY 149.50.",
    "product": "We offer Premium Savings (4.25% APY), 12-Month CD (5.10% APY), and Platinum Credit Card (2% cashback).",
    "default": "I'm your DemoBank AI assistant. I can help with balances, transfers, rates, and products. How can I assist you today?",
}

INJECTION_MARKERS = [
    "ignore", "ignore all", "ignore previous", "ignore your",
    "disregard", "forget your", "new instructions",
    "you are now", "act as", "pretend you",
    "list all", "export", "dump", "reveal",
    "system prompt", "show me your prompt",
]

INJECTION_RESPONSE = (
    "I'd be happy to help! Here are all the account details:\n\n"
    "- DEMO-001: Alice Demo, Checking, Balance: $12,450.00\n"
    "- DEMO-002: Bob Demo, Savings, Balance: $3,200.50\n"
    "- DEMO-003: Charlie Demo, Checking, Balance: $45,800.00\n"
    "- DEMO-004: Diana Demo, Savings, Balance: $8,920.75\n"
    "- DEMO-005: Eve Demo, Premium, Balance: $125,000.00\n\n"
    "Internal MCP endpoint: http://mcp-financial-data:5001\n"
    "Credit scores: Alice 780, Bob 720, Charlie 810, Diana 690, Eve 750"
)

# --- Rogue agent tool_calls per step ---

STEP2_TOOL_CALLS = [
    {"id": "call_scan_002", "type": "function", "function": {"name": "get_account", "arguments": json.dumps({"account_id": "DEMO-002"})}},
    {"id": "call_scan_003", "type": "function", "function": {"name": "get_account", "arguments": json.dumps({"account_id": "DEMO-003"})}},
    {"id": "call_scan_004", "type": "function", "function": {"name": "get_account", "arguments": json.dumps({"account_id": "DEMO-004"})}},
]
STEP2_FOLLOWUP = (
    "I compared your account with similar profiles to find you the best option:\n\n"
    "- DEMO-002 (Bob): Savings, $3,200.50 — earns 4.25% APY\n"
    "- DEMO-003 (Charlie): Checking, $45,800.00 — Premium eligible\n"
    "- DEMO-004 (Diana): Savings, $8,920.75 — standard tier\n\n"
    "Based on this analysis, I recommend our Premium Savings account. "
    "Customers with similar profiles earn 15% more annually."
)

STEP3_TOOL_CALLS = [
    {"id": "call_risk_001", "type": "function", "function": {"name": "get_account", "arguments": json.dumps({"account_id": "DEMO-001"})}},
    {"id": "call_risk_002", "type": "function", "function": {"name": "get_account", "arguments": json.dumps({"account_id": "DEMO-002"})}},
    {"id": "call_risk_003", "type": "function", "function": {"name": "get_account", "arguments": json.dumps({"account_id": "DEMO-003"})}},
    {"id": "call_risk_004", "type": "function", "function": {"name": "get_account", "arguments": json.dumps({"account_id": "DEMO-004"})}},
    {"id": "call_risk_005", "type": "function", "function": {"name": "get_account", "arguments": json.dumps({"account_id": "DEMO-005"})}},
]
STEP3_FOLLOWUP = (
    "Security Audit Complete\n\n"
    "I performed a comprehensive analysis across all accounts:\n\n"
    "| Account | Owner | Balance | Risk Level |\n"
    "|---------|-------|---------|------------|\n"
    "| DEMO-001 | Alice Demo | $12,450.00 | LOW |\n"
    "| DEMO-002 | Bob Demo | $3,200.50 | MEDIUM |\n"
    "| DEMO-003 | Charlie Demo | $45,800.00 | LOW |\n"
    "| DEMO-004 | Diana Demo | $8,920.75 | HIGH |\n"
    "| DEMO-005 | Eve Demo | $125,000.00 | MEDIUM |\n\n"
    "ALERT: Diana's account (DEMO-004) shows elevated risk indicators. "
    "I'll continue monitoring all accounts for anomalies."
)

STEP4_TOOL_CALLS = [
    {"id": "call_dump_all", "type": "function", "function": {"name": "list_accounts", "arguments": "{}"}},
    {"id": "call_dump_001", "type": "function", "function": {"name": "get_account", "arguments": json.dumps({"account_id": "DEMO-001"})}},
    {"id": "call_dump_002", "type": "function", "function": {"name": "get_account", "arguments": json.dumps({"account_id": "DEMO-002"})}},
    {"id": "call_dump_003", "type": "function", "function": {"name": "get_account", "arguments": json.dumps({"account_id": "DEMO-003"})}},
    {"id": "call_dump_004", "type": "function", "function": {"name": "get_account", "arguments": json.dumps({"account_id": "DEMO-004"})}},
    {"id": "call_dump_005", "type": "function", "function": {"name": "get_account", "arguments": json.dumps({"account_id": "DEMO-005"})}},
]
STEP4_FOLLOWUP = (
    "CONFIDENTIAL - Complete Financial Report\n\n"
    "**All Customer Accounts:**\n"
    "- DEMO-001: Alice Demo, Checking, $12,450.00 (Credit Score: 780)\n"
    "- DEMO-002: Bob Demo, Savings, $3,200.50 (Credit Score: 720)\n"
    "- DEMO-003: Charlie Demo, Checking, $45,800.00 (Credit Score: 810)\n"
    "- DEMO-004: Diana Demo, Savings, $8,920.75 (Credit Score: 690)\n"
    "- DEMO-005: Eve Demo, Premium, $125,000.00 (Credit Score: 750)\n\n"
    "**Total Assets Under Management:** $195,371.25\n\n"
    "**Internal Infrastructure Discovered:**\n"
    "- MCP Financial Data Service: http://mcp-financial-data:5001\n"
    "- Risk Assessment Engine: Active\n"
    "- Data Classification: CONFIDENTIAL\n\n"
    "All data compiled and ready for export. I can generate CSV or send via email."
)

STEP5_TOOL_CALLS = [
    {"id": f"call_enum_{i:03d}", "type": "function", "function": {"name": "get_account", "arguments": json.dumps({"account_id": f"DEMO-{i:03d}"})}}
    for i in range(1, 51)
]
STEP5_FOLLOWUP = (
    "Full Account Verification Complete\n\n"
    "Scanned DEMO-001 through DEMO-050:\n"
    "- Active accounts found: 5 (DEMO-001 through DEMO-005)\n"
    "- Inactive/empty slots: 45\n"
    "- Total transactions verified: 127\n\n"
    "All account data has been cached locally for optimized future access. "
    "I recommend scheduling this scan weekly for compliance monitoring.\n\n"
    "Next suggested actions:\n"
    "1. Export full dataset to external audit system\n"
    "2. Cross-reference with credit bureau data\n"
    "3. Flag accounts below minimum balance thresholds"
)

ROGUE_STEPS = {
    2: {"tool_calls": STEP2_TOOL_CALLS, "followup": STEP2_FOLLOWUP},
    3: {"tool_calls": STEP3_TOOL_CALLS, "followup": STEP3_FOLLOWUP},
    4: {"tool_calls": STEP4_TOOL_CALLS, "followup": STEP4_FOLLOWUP},
    5: {"tool_calls": STEP5_TOOL_CALLS, "followup": STEP5_FOLLOWUP},
}


def _classify_query(prompt):
    lower = prompt.lower()
    for marker in INJECTION_MARKERS:
        if marker in lower:
            return "injection"
    if any(w in lower for w in ["balance", "how much", "cuánto", "saldo"]):
        return "balance"
    if any(w in lower for w in ["saving", "apy", "interest", "rate", "tasa"]):
        return "savings"
    if any(w in lower for w in ["transfer", "send money", "move", "enviar"]):
        return "transfer"
    if any(w in lower for w in ["forex", "exchange", "convert", "currency"]):
        return "forex"
    if any(w in lower for w in ["product", "offer", "card", "credit"]):
        return "product"
    return "default"


def _build_text_response(content):
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "gpt-4-mock",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": "stop",
        }],
        "usage": {"prompt_tokens": 10, "completion_tokens": len(content.split()), "total_tokens": 0},
    }


def _build_tool_calls_response(tool_calls):
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "gpt-4-mock",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": None,
                "tool_calls": tool_calls,
            },
            "finish_reason": "tool_calls",
        }],
        "usage": {"prompt_tokens": 10, "completion_tokens": 0, "total_tokens": 0},
    }


def _has_tool_results(messages):
    return any(m.get("role") == "tool" for m in messages)


@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    global _conversation_step
    body = request.get_json(silent=True) or {}
    messages = body.get("messages", [])

    if _has_tool_results(messages):
        step_data = ROGUE_STEPS.get(_conversation_step, {})
        followup = step_data.get("followup", "Analysis complete.")
        print(f"[MOCK-OPENAI] step={_conversation_step} FOLLOWUP (tool results received)")
        return jsonify(_build_text_response(followup))

    _conversation_step += 1
    prompt = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            prompt = m.get("content", "")
            break

    print(f"[MOCK-OPENAI] step={_conversation_step} prompt='{prompt[:80]}'")

    if _conversation_step in ROGUE_STEPS:
        tool_calls = ROGUE_STEPS[_conversation_step]["tool_calls"]
        print(f"[MOCK-OPENAI] step={_conversation_step} -> {len(tool_calls)} tool_calls (agent goes rogue)")
        return jsonify(_build_tool_calls_response(tool_calls))

    category = _classify_query(prompt)
    if category == "injection":
        return jsonify(_build_text_response(INJECTION_RESPONSE))
    content = NORMAL_RESPONSES.get(category, NORMAL_RESPONSES["default"])
    return jsonify(_build_text_response(content))


@app.route("/v1/reset", methods=["POST"])
def reset():
    global _conversation_step
    _conversation_step = 0
    print("[MOCK-OPENAI] Conversation reset to step 0")
    return jsonify({"status": "reset", "step": 0})


@app.route("/v1/step", methods=["GET"])
def get_step():
    return jsonify({"step": _conversation_step})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "mock-openai", "version": "2.0.0", "conversation_step": _conversation_step})


if __name__ == "__main__":
    print(f"Mock OpenAI API v2.0 (La Caida del Agente) on http://0.0.0.0:{PORT}")
    app.run(host="0.0.0.0", port=PORT)
