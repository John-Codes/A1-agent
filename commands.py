import agent
from embedding_commands import run_embedding_command
from llm_commands import run_llm_command
from tools import tool_names
from tools.log import log_exception, report_tool_failure

EXIT_COMMANDS = {"/quit", "/exit", "/q"}


def run(text):
    text = (text or "").strip()
    if not text:
        return {"kind": "empty", "text": ""}

    command, body = _split(text)
    if command == '/cdl_articles':
        from lib.features.cdl_articles.client import run as article_command
        from tools.dispatcher import _safe_tool
        return {'kind': 'tool', 'response': _safe_tool('cdl_articles', article_command, body), 'error': None}
    if command == '/cdl_keywords':
        from tools.seo_registry import run_seo_registry
        try:
            return {'kind': 'text', 'text': run_seo_registry(body, 'cdl_keywords')}
        except Exception as exc:
            log_exception('cdl_keywords', exc)
            return {'kind': 'error', 'error': report_tool_failure('cdl_keywords', exc)}
    if command == '/seo':
        from seo.service import command as seo_command, service as seo_service
        try:
            seo_service.start()
            return {'kind': 'text', 'text': seo_command(body)}
        except Exception as exc:
            log_exception('daily_seo', exc)
            return {'kind': 'error', 'error': report_tool_failure('daily_seo', exc)}
    if command in EXIT_COMMANDS:
        return {"kind": "exit", "category": "info", "text": "bye"}
    if command == "/tick":
        return {"kind": "tick", **agent.tick()}
    if command == "/memory":
        return {"kind": "text", "category": "data", "text": agent.memory()}
    if command == "/log":
        return {"kind": "text", "category": "data", "text": agent.log()}
    if command == "/tools":
        return {"kind": "text", "category": "data", "text": "\n".join(tool_names())}
    if command in {"/llm", "/provider"}:
        return {"kind": "text", "text": run_llm_command(body)}
    if command == "/embedding":
        return {"kind": "text", "text": run_embedding_command(body)}
    if command == "/history":
        return _tool("conversation_history", body)
    if command == "/search":
        return _tool("web_search", body)
    if command.startswith("/") and command[1:] in tool_names():
        return _tool(command[1:], body)
    if command.startswith("/"):
        return {"kind": "error", "error": f"Unknown command: {command}"}
    return {"kind": "message", **agent.message(text)}


def _tool(name, body):
    try:
        return {"kind": "tool", "response": agent.tool(name, body), "error": None}
    except Exception as exc:
        return {"kind": "tool", "response": "", "error": str(exc)}


def _split(text):
    parts = text.split(maxsplit=1)
    command = parts[0].lower()
    body = parts[1].strip() if len(parts) > 1 else ""
    return command, body
