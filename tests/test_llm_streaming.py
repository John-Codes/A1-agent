import asyncio
import json
from unittest.mock import Mock

import api
import llm_client
from api_models import TextBody
from llm_provider_calls import _consume_ollama_stream


def _chunk(kind, text):
    return {"type": "chunk", "kind": kind, "text": text}


def test_consume_ollama_stream_emits_chunks_and_joins():
    response = Mock()
    response.iter_lines.return_value = [
        json.dumps({"message": {"thinking": "Think "}}),
        json.dumps({"message": {"content": "Hello "}}),
        json.dumps({"message": {"content": "world."}, "done": True}),
    ]
    seen = []
    text = _consume_ollama_stream(response, True, seen.append)
    assert text == "<think>Think</think>\nHello world."
    assert seen == [
        {"kind": "thinking", "text": "Think "},
        {"kind": "content", "text": "Hello "},
        {"kind": "content", "text": "world."},
    ]


def _worker_streams_chunks(prompt, route, image_data, queue):
    queue.put(_chunk("content", "Hel"))
    queue.put(_chunk("content", "lo"))
    queue.put({"ok": True, "text": "Hello"})


def test_try_route_streams_chunks_to_callback(monkeypatch):
    monkeypatch.setattr(llm_client, "_route_worker", _worker_streams_chunks)
    seen = []
    result = llm_client._try_route(
        "p", {"provider": "test", "model": "test"}, "", on_chunk=seen.append
    )
    assert result["ok"] is True
    assert [item["text"] for item in seen] == ["Hel", "lo"]
    assert all(item["type"] == "chunk" for item in seen)


def test_complete_prompt_relays_reset_and_buffers_chunks(monkeypatch):
    events = []
    shared = {"stream_callback": events.append}

    def fake_try(prompt, route, image_data, on_chunk):
        on_chunk({"type": "reset"})
        on_chunk(_chunk("content", "Hi"))
        return {"ok": True, "text": "Hi", "provider": "test",
                "model": "m", "api_base": "", "error": None}

    monkeypatch.setattr(
        llm_client, "active_routes",
        lambda s: [{"label": "default", "provider": "test", "model": "m", "api_base": ""}],
    )
    monkeypatch.setattr(llm_client, "_try_route", fake_try)
    result = llm_client.complete_prompt("p", shared)
    assert result["ok"] is True
    assert shared["pending_stream"] == [{"kind": "content", "text": "Hi"}]
    assert {"type": "reset"} in events
    assert _chunk("content", "Hi") in events


def test_stream_relay_survives_broken_callback(monkeypatch):
    def boom(item):
        raise OSError("pipe closed")

    shared = {"stream_callback": boom}
    relay = llm_client._stream_relay(shared)
    relay(_chunk("content", "still works"))
    assert shared["pending_stream"] == [{"kind": "content", "text": "still works"}]


def test_message_stream_endpoint_emits_sse(monkeypatch):
    def fake_message(text, session_id="", user_message="", image_data="", on_chunk=None):
        if on_chunk:
            on_chunk(_chunk("content", "Hi"))
        return {
            "speaker": "master_llm", "response": "Hi", "streamed": bool(on_chunk),
            "error": None, "llm_error": None, "llm_attempts": [],
            "llm_fallback_used": False, "embedding_error": None, "embedding_attempts": [],
        }

    monkeypatch.setattr(api.agent, "message", fake_message)
    response = api.message_stream(TextBody(text="hi"))

    async def _collect(iterator):
        return [part async for part in iterator]

    parts = asyncio.run(_collect(response.body_iterator))
    body = "".join(part.decode() if isinstance(part, bytes) else part for part in parts)
    assert body.startswith("data: ")
    assert '"type": "chunk"' in body
    assert '"type": "result"' in body
    assert '"streamed": true' in body
