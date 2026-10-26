from fastapi.testclient import TestClient

from openai_chat.main import app

client = TestClient(app)


def test_health_without_api_key(monkeypatch) -> None:
    monkeypatch.delenv("CHAT_API_KEY", raising=False)
    monkeypatch.delenv("CHAT_MODEL", raising=False)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "openai_configured": False,
        "model": "gpt-4.1-mini",
    }


def test_home_page() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "OpenAI Chat" in response.text


def test_chat_requires_api_key(monkeypatch) -> None:
    monkeypatch.delenv("CHAT_API_KEY", raising=False)
    response = client.post(
        "/api/chat",
        json={"messages": [{"role": "user", "content": "Hello"}]},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "CHAT_API_KEY is not configured for this environment."


def test_chat_validates_empty_messages() -> None:
    response = client.post("/api/chat", json={"messages": []})

    assert response.status_code == 422
