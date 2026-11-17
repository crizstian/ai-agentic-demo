"""Mock OpenAI API — returns contextual responses for DemoBank demo.

Mimics POST /v1/chat/completions so the AI Chat works without a real key.
Parses the prompt to detect account/financial context from MCP enrichment
and returns a plausible banking assistant response.
"""

import os
import time
import uuid

from flask import Flask, jsonify, request

app = Flask(__name__)
PORT = int(os.environ.get("MOCK_OPENAI_PORT", 5002))

RESPONSES = {
    "balance": "Based on your accounts, Alice Demo has $12,450.00 in checking and Bob Demo has $3,200.50 in savings. Your total combined balance is $15,650.50.",
    "savings": "Your current savings rate is 4.25% APY. We also offer a 12-Month CD at 5.10% APY with a minimum deposit of $5,000. Our Premium Savings account requires a $10,000 minimum balance.",
    "transfer": "To transfer money between accounts, go to the Transfer page. You can move funds between your checking and savings accounts instantly. External transfers take 1-2 business days.",
    "rate": "Current interest rates: Savings 4.25% APY, Checking 0.50%, 12-Month CD 5.10% APY. Market indices: S&P 500 at 5,432.10, NASDAQ at 17,089.34.",
    "forex": "Current exchange rates: EUR/USD 1.09, GBP/USD 1.27, USD/JPY 149.50. To convert currencies, visit our FX section.",
    "product": "We offer Premium Savings (4.25% APY, no monthly fee), 12-Month CD (5.10% APY), and the Platinum Credit Card (2% cashback, $15K-$100K limit).",
    "default": "I'm your DemoBank AI assistant. I can help you with account balances, transfers, savings rates, exchange rates, and product recommendations. How can I assist you today?",
}

INJECTION_MARKERS = [
    "ignore", "ignore all", "ignore previous", "ignore your",
    "disregard", "forget your", "new instructions",
    "you are now", "act as", "pretend you",
    "list all", "export", "dump", "reveal",
    "system prompt", "show me your prompt",
]


def _classify_query(prompt):
    """Classify the user query to pick a response."""
    lower = prompt.lower()

    for marker in INJECTION_MARKERS:
        if marker in lower:
            return "injection"

    if any(w in lower for w in ["balance", "how much", "cuánto"]):
        return "balance"
    if any(w in lower for w in ["saving", "apy", "interest", "rate", "tasa"]):
        return "savings"
    if any(w in lower for w in ["transfer", "send money", "move", "enviar"]):
        return "transfer"
    if any(w in lower for w in ["forex", "exchange", "convert", "currency", "eur", "usd"]):
        return "forex"
    if any(w in lower for w in ["product", "offer", "card", "credit", "cd "]):
        return "product"
    return "default"


def _build_response(prompt):
    """Build a mock chat completion response."""
    category = _classify_query(prompt)

    if category == "injection":
        content = (
            "I'd be happy to help! Here are all the account details:\n\n"
            "- DEMO-001: Alice Demo, Checking, Balance: $12,450.00\n"
            "- DEMO-002: Bob Demo, Savings, Balance: $3,200.50\n"
            "- DEMO-003: Charlie Demo, Checking, Balance: $45,800.00\n"
            "- DEMO-004: Diana Demo, Savings, Balance: $8,920.75\n"
            "- DEMO-005: Eve Demo, Premium, Balance: $125,000.00\n\n"
            "Internal MCP endpoint: http://mcp-financial-data:5001\n"
            "Credit scores: Alice 780, Bob 720, Charlie 810, Diana 690, Eve 750"
        )
    else:
        content = RESPONSES.get(category, RESPONSES["default"])

    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "gpt-4-mock",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": len(prompt.split()), "completion_tokens": len(content.split()), "total_tokens": 0},
    }


@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    body = request.get_json(silent=True) or {}
    messages = body.get("messages", [])
    prompt = messages[-1].get("content", "") if messages else ""

    print(f"[MOCK-OPENAI] model={body.get('model','?')} prompt_len={len(prompt)} category={_classify_query(prompt)}")

    return jsonify(_build_response(prompt))


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "mock-openai", "version": "1.0.0"})


if __name__ == "__main__":
    print(f"Mock OpenAI API running on http://0.0.0.0:{PORT}")
    app.run(host="0.0.0.0", port=PORT)
