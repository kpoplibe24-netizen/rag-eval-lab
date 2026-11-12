import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client(tmp_path, monkeypatch):

    # Use a temporary database for tests.
    monkeypatch.setattr(
        main.config,
        "DB_PATH",
        str(tmp_path / "test.db")
    )

    # Avoid loading the real retrieval models.
    monkeypatch.setattr(
        main.config,
        "load_threshold",
        lambda: 3.527
    )

    async def fake_retrieve(question):
        if question == "unanswerable question":
            return [
                {
                    "file": "test.md",
                    "heading": "Test",
                    "text": "Unrelated content",
                    "score": 1.0
                }
            ]

        return [
            {
                "file": "test.md",
                "heading": "Introduction",
                "text": "FastAPI is a Python web framework.",
                "score": 4.0
            }
        ]

    async def fake_generate_answer(question, chunks):
        return "FastAPI is a Python web framework. [1]"

    monkeypatch.setattr(main, "retrieve", fake_retrieve)
    monkeypatch.setattr(main, "generate_answer", fake_generate_answer)

    main.cache.clear()

    with TestClient(main.app) as test_client:
        yield test_client

    main.cache.clear()


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_successful_answer(client):
    response = client.post(
        "/ask",
        json={"question": "What is FastAPI?"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["refused"] is False
    assert data["cached"] is False
    assert len(data["sources"]) > 0
    assert data["answer"] == "FastAPI is a Python web framework. [1]"


def test_cache_hit(client):
    question = "What is FastAPI?"

    first = client.post("/ask", json={"question": question})
    second = client.post("/ask", json={"question": question})

    assert first.status_code == 200
    assert second.status_code == 200

    assert first.json()["cached"] is False
    assert second.json()["cached"] is True
    assert second.json()["answer"] == first.json()["answer"]


def test_refusal(client):
    response = client.post(
        "/ask",
        json={"question": "unanswerable question"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["refused"] is True
    assert data["sources"] == []
    assert data["cached"] is False


def test_question_too_short(client):
    response = client.post(
        "/ask",
        json={"question": "Hi"}
    )

    assert response.status_code == 422


def test_llm_failure(client, monkeypatch):

    async def failing_generate_answer(question, chunks):
        raise Exception("LLM unavailable")

    monkeypatch.setattr(
        main,
        "generate_answer",
        failing_generate_answer
    )

    response = client.post(
        "/ask",
        json={"question": "What is FastAPI?"}
    )

    assert response.status_code == 502


def test_stats(client):
    client.post(
        "/ask",
        json={"question": "What is FastAPI?"}
    )

    response = client.get("/stats")

    assert response.status_code == 200

    data = response.json()

    assert "overall" in data
    assert "latency_answered" in data
    assert data["overall"]["total_queries"] == 1