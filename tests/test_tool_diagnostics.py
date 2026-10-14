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
    assert shared["last_error"] == "BaseNode: all LLM routes failed. Details: gateway.log"
    saved = path.read_text()
    assert "Traceback" in saved and "details " * 200 in saved
    assert "secret-test-key-value" not in saved
    assert "[REDACTED]" in saved


def test_tool_failure_does_not_expose_traceback(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(log, "LOG_PATH", tmp_path / "gateway.log")
    def fail(body):
        raise RuntimeError('AgentMail 403: {"message":"Forbidden"}')
    result = dispatcher._safe_tool("agentmail", fail, "")
    assert result == "agentmail: access denied; check the API key or permissions. Details: gateway.log"
    assert capsys.readouterr().out == ""
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
    assert log.brief_error("browser_use", TimeoutError()) == "browser_use: request timed out. Details: gateway.log"
