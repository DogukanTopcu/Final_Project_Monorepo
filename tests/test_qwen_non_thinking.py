from __future__ import annotations

import requests

from core.models import OpenAICompatibleModel
from core.prompt import open_prompt
from core.types import Query


class _FakeResponse:
    headers: dict = {}

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return {
            "choices": [{"message": {"content": "hello"}, "logprobs": {"content": []}}],
            "usage": {"prompt_tokens": 4, "completion_tokens": 1},
        }


def test_qwen_requests_disable_thinking(monkeypatch):
    captured: dict = {}

    def fake_post(url: str, json: dict, headers: dict, timeout: float):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        captured["timeout"] = timeout
        return _FakeResponse()

    monkeypatch.setattr(requests, "post", fake_post)

    model = OpenAICompatibleModel(
        model_id="Qwen/Qwen3.5-4B",
        base_url="http://example.com/v1",
    )
    text, confidence, in_tok, out_tok, cost = model.generate("hey", max_tokens=32)

    assert text == "hello"
    assert confidence == 0.5
    assert in_tok == 4
    assert out_tok == 1
    assert cost == 0.0
    assert captured["json"]["chat_template_kwargs"] == {"enable_thinking": False}


def test_open_prompt_encourages_chain_of_thought():
    query = Query(id="q1", text="2+2?", answer="4")
    prompt = open_prompt(query)
    assert "step-by-step" in prompt
    assert "Answer: <number>" in prompt
