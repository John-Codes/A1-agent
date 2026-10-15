from unittest.mock import patch

from nodes.base import BaseNode
from tools import dispatcher
from tools import log
from tools import web


def test_exception_is_short_on_console_and_complete_in_log(tmp_path, capsys, monkeypatch):
    path = tmp_path / "gateway.log"
    monkeypatch.setattr(log, "LOG_PATH", path)
    monkeypatch.setenv("TEST_API_KEY", "secret-test-key-value")
    shared = {}
    try:
        raise RuntimeError("LLM failed\nprovider: example\nsecret-test-key-value\n" + "details " * 200)
    except RuntimeError as exc:
        BaseNode()._record_exception(shared, exc)
    assert capsys.readouterr().out == ""
    assert shared["last_error"] == f"Tool BaseNode failed: all LLM routes failed. Check log for more info @ {path}"
    saved = path.read_text()
    assert "Traceback" in saved and "details " * 200 in saved
    assert "secret-test-key-value" not in saved
    assert "[REDACTED]" in saved


def test_tool_failure_does_not_expose_traceback(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(log, "LOG_PATH", tmp_path / "gateway.log")
    def fail(body):
        raise RuntimeError('AgentMail 403: {"message":"Forbidden"}')
    result = dispatcher._safe_tool("agentmail", fail, "")
    assert "Tool agentmail failed: access denied" in result
    assert str(tmp_path / "gateway.log") in result
    assert capsys.readouterr().out.strip() == result
    assert "Traceback" in (tmp_path / "gateway.log").read_text()


def test_full_tool_result_logged_without_console_noise(tmp_path, capsys, monkeypatch):
    path = tmp_path / "gateway.log"
    monkeypatch.setattr(log, "LOG_PATH", path)
    detail = "first line\n" + "long result " * 200
    log.log_tool_event("memory_search", "done", detail)
    assert detail in path.read_text()
    assert capsys.readouterr().out == ""


def test_nested_tool_tag_removed_from_search():
    with patch.object(web, "_try_backend", return_value="Backend: test") as call:
        assert web.run_web_search('<tool name="web_search">Python official website') == "Backend: test"
        assert call.call_args.args[1] == "Python official website"


def test_empty_timeout_has_a_useful_short_message():
    assert log.brief_error("browser_use", TimeoutError()) == f"Tool browser_use failed: request timed out. Check log for more info @ {log.LOG_PATH.resolve()}"


def test_model_failure_prints_even_when_fallback_succeeds(tmp_path, monkeypatch, capsys):
    import llm_client
    monkeypatch.setattr(log, 'LOG_PATH', tmp_path / 'custom.log')
    monkeypatch.setattr(llm_client, 'active_routes', lambda shared: [
        {'provider': 'openrouter', 'model': 'failed-model', 'label': 'default'},
        {'provider': 'ollama', 'model': 'working-model', 'label': 'fallback_1'}])
    responses = iter([
        {'ok': False, 'error': {'type': 'TimeoutError', 'message': 'Exceeded 120s'}},
        {'ok': True, 'text': 'done', 'provider': 'ollama', 'model': 'working-model'}])
    monkeypatch.setattr(llm_client, '_try_route', lambda *args: next(responses))
    assert llm_client.complete_prompt('test', {})['ok']
    out = capsys.readouterr().out
    assert 'MODEL FAILED | openrouter/failed-model' in out
    assert 'Exceeded 120s' in out
    assert str(tmp_path / 'custom.log') in out
    assert 'working-model' not in out


def test_structured_tool_failure_prints_log_path(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(log, 'LOG_PATH', tmp_path / 'custom.log')
    result = dispatcher._logged_result('article_save', {'ok': False, 'error': 'rejected'})
    assert 'Tool article_save failed' in result
    assert str(tmp_path / 'custom.log') in capsys.readouterr().out


def test_unknown_tool_prints_and_preserves_exception(tmp_path, monkeypatch, capsys):
    import pytest
    from store import store
    monkeypatch.setitem(store, 'mode', 'execute')
    monkeypatch.setattr(log, 'LOG_PATH', tmp_path / 'custom.log')
    with pytest.raises(ValueError, match='Unknown tool'):
        dispatcher.dispatch_tool_call({'name': 'missing_tool', 'body': ''})
    assert 'Tool missing_tool failed' in capsys.readouterr().out
