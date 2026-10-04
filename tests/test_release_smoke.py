import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.agent_loop import is_calculation_request, is_multi_step_request, is_time_request
from agent import planner
from agent import ollama_client
from agent.learning import extract_learning_strategy
from agent.lesson_retriever import retrieve_similar_lessons
from agent.plan_executor import execute_tool_step
from app.main import app
from memory.memory import get_lessons, init_db, save_lesson


@pytest.fixture(scope="module")
def seeded_lessons():
    init_db()
    save_lesson(
        "Calculate 500 * 8 using the calculator tool.",
        "Tool execution failed: calculator unavailable.",
        1,
        "NO",
        "Retry a failed tool operation before abandoning the task.",
        "ERROR_RECOVERY",
    )
    return get_lessons()


def test_calculator_detection():
    assert is_calculation_request("What is 600 * 9?") is True


def test_tell_me_time_is_a_multi_step_operation():
    request = "Calculate 100 / 4 and tell me the time."
    assert is_time_request(request) is True
    assert is_multi_step_request(request) is True


def test_planner_uses_fallback_when_provider_is_unavailable(monkeypatch):
    monkeypatch.setattr(planner, "is_llm_available", lambda: False)
    plan = planner.create_plan("Calculate 100 / 4 and tell me the time.")
    assert plan == "1. Calculate 100 / 4\n2. Get the current time"


def test_openai_provider_uses_backend_environment_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "unit-test-only")

    class FakeOpenAI:
        def __init__(self, api_key, timeout):
            assert api_key == "unit-test-only"
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=self.create_completion)
            )

        def create_completion(self, model, messages):
            assert model == "gpt-4o-mini"
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="OpenAI reply"))]
            )

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=FakeOpenAI))
    assert ollama_client.is_llm_available() is True
    assert ollama_client.chat_completion("llama3.2", [{"role": "user", "content": "Hi"}]) == "OpenAI reply"

    response = TestClient(app).get("/health")
    assert response.json()["llm_provider"] == "openai"
    assert response.json()["llm_available"] is True
    assert "unit-test-only" not in response.text


def test_calculator_execution():
    result = execute_tool_step("What is 600 * 9?", learning_strategy="")
    assert result["success"] is True
    assert result["result"] == 5400


def test_learning_strategy_retrieval(seeded_lessons):
    retrieved = retrieve_similar_lessons("Calculate 750 * 6 using the calculator tool.", seeded_lessons, top_k=5)
    assert len(retrieved) >= 1
    strategy = extract_learning_strategy("Calculate 750 * 6 using the calculator tool.", retrieved)
    assert isinstance(strategy, str)
    assert "LEARNED_STRATEGY:" in strategy


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "ollama_available" in data


def test_chat_calculator_request():
    client = TestClient(app)
    response = client.post("/chat", json={"message": "What is 600 * 9?"})
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "5400"
    assert "Detected calculation task" in data["activity"]
    assert "Executed Calculator tool" in data["activity"]
