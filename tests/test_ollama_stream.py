import json
from unittest.mock import Mock

from llm_provider_calls import _read_ollama_stream


def test_ollama_stream_keeps_thinking_and_answer():
    response = Mock()
    response.iter_lines.return_value = [
        json.dumps({"message": {"thinking": "First "}}),
        json.dumps({"message": {"thinking": "thought."}}),
        json.dumps({"message": {"content": "Final "}}),
        json.dumps({"message": {"content": "answer."}, "done": True}),
    ]
    assert _read_ollama_stream(response, True) == "<think>First thought.</think>\nFinal answer."


def test_ollama_stream_content_only_for_fast_model():
    response = Mock()
    response.iter_lines.return_value = [json.dumps({"message": {"content": "OK"}})]
    assert _read_ollama_stream(response, False) == "OK"
