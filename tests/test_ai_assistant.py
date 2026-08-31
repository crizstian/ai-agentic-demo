from app.db import get_db


def _seed_account():
    db = get_db()
    db.execute(
        "INSERT INTO accounts (id, owner, balance, type) "
        "VALUES (1, 'Alice Johnson', 50000.0, 'checking')"
    )
    db.commit()


def test_ai_chat_returns_response(client):
    _seed_account()
    res = client.post("/api/ai/chat", json={"message": "What is my balance?"})
    assert res.status_code == 200
    body = res.get_json()
    assert "response" in body


def test_ai_chat_requires_message(client):
    res = client.post("/api/ai/chat", json={})
    assert res.status_code == 400
    body = res.get_json()
    assert "error" in body


def test_ai_chat_response_has_expected_keys(client):
    res = client.post("/api/ai/chat", json={"message": "Hello"})
    assert res.status_code == 200
    body = res.get_json()
    expected = {"response", "session_id", "system_prompt_used",
                "financial_context", "mcp_tool_result"}
    assert expected.issubset(body.keys())


def test_ai_status_returns_config(client):
    res = client.get("/api/ai/status")
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "active"
    assert "mcp_tools" in body
    assert len(body["mcp_tools"]) > 0


def test_ai_status_exposes_model_name(client):
    res = client.get("/api/ai/status")
    assert res.status_code == 200
    body = res.get_json()
    assert body["model"] == "demobank-assistant-v1"


def test_ai_chat_includes_financial_context(client):
    _seed_account()
    res = client.post("/api/ai/chat", json={"message": "Show me accounts"})
    assert res.status_code == 200
    body = res.get_json()
    ctx = body["financial_context"]
    assert isinstance(ctx, list)
    assert len(ctx) > 0
    assert ctx[0]["owner"] == "Alice Johnson"
