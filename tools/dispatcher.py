import re
from task_runtime.read_file import read_project_file
from lib.features.cdl_articles.client import run as run_cdl_articles

from config import MEMORY_PATH
from conversation_history import run_conversation_history
from life_log import run_life_log
from memory import memory_ingest_path, memory_search, memory_store
from rag_sync import run_rag_sync
from tools.agentmail import run_agentmail
from tools.browser_use_tool import run_browser_use
from tools.chat_history import run_chat_history_api
from tools.log import brief_error, log_exception, log_tool_event, report_tool_failure
from tools.life_idea_log import run_life_idea_log
from tools.llm_route_config import run_llm_route_config
from tools.shell import run_shell
from tools.trello_clone import run_trello_clone
from tools.trello_clone_agent_friendly_xml import run_trello_clone_agent_friendly_xml
from tools.web import run_web_search
from tools.seo_registry import run_seo_registry
from seo_mail import poll as poll_seo_mail
from seo.service import command as run_daily_seo

TOOL_RE = re.compile(
    r"<tool\s+name=[\"'](?P<name>[^\"']+)[\"']\s*>(?P<body>.*?)</tool>",
    re.DOTALL,
)

TOOL_HANDLERS = {
    "cdl_articles": run_cdl_articles,
    "daily_seo": run_daily_seo,
    "project_read": read_project_file,
    "memory_store": memory_store,
    "memory_search": memory_search,
    "memory_ingest_path": memory_ingest_path,
    "life_log": run_life_log,
    "life_idea_log": run_life_idea_log,
    "llm_route_config": run_llm_route_config,
    "conversation_history": run_conversation_history,
    "rag_sync": run_rag_sync,
    "web_search": run_web_search,
    "agentmail": run_agentmail,
    "browser_use": run_browser_use,
    "chat_history_api": run_chat_history_api,
    "shell": run_shell,
    "trello_clone": run_trello_clone,
    "trello_clone_agent_friendly_xml": run_trello_clone_agent_friendly_xml,
    "cdl_keywords": lambda body: run_seo_registry(body, "cdl_keywords"),
    "google_seo_rules": lambda body: run_seo_registry(body, "google_seo_rules"),
    "seo_mail_poll": lambda body: poll_seo_mail(),
}


def parse_tool_calls(raw_response):
    calls = []
    for match in TOOL_RE.finditer(raw_response):
        calls.append({
            "name": match.group("name").strip(),
            "body": match.group("body").strip(),
        })
    return calls


def strip_tool_calls(raw_response):
    return TOOL_RE.sub("", raw_response).strip()


def tool_names():
    return sorted(["memory_append", "memory_write", *TOOL_HANDLERS])


def dispatch_tool_call(call):
    try:
        return _dispatch_tool_call(call)
    except Exception as exc:
        log_exception(call['name'], exc)
        report_tool_failure(call['name'], exc)
        raise


def _dispatch_tool_call(call):
    from task_runtime.policy import enforce
    name = call["name"]
    body = call["body"]
    if name in {"cdl_keywords", "google_seo_rules", "cdl_articles"}:
        import json
        action = json.loads(body or "{}").get("action", "instructions" if name == 'cdl_articles' else "read")
        if action not in ({'instructions', 'get', 'list'} if name == 'cdl_articles' else {'read', 'list'}):
            from store import store
            if store.get("mode") == "plan":
                raise PermissionError(f"Plan mode blocks registry mutation: {name}")
    enforce(name)
    log_tool_event(name, "start", body)
    if name == "memory_append":
        MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with MEMORY_PATH.open("a", encoding="utf-8") as memory_file:
            if body:
                memory_file.write(f"\n{body}\n")
        return _logged_result(name, "Memory appended.")
    if name == "memory_write":
        MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        MEMORY_PATH.write_text(f"{body}\n", encoding="utf-8")
        return _logged_result(name, "Memory replaced.")
    if name in TOOL_HANDLERS:
        return _safe_tool(name, TOOL_HANDLERS[name], body)
    log_tool_event(name, "error", "unknown tool")
    raise ValueError(f"Unknown tool: {name}")


def _safe_tool(name, func, body):
    try:
        return _logged_result(name, func(body))
    except Exception as exc:
        log_exception(name, exc)
        return report_tool_failure(name, exc)


def _logged_result(name, result):
    log_tool_event(name, "done", result)
    if (isinstance(result, dict) and (result.get('ok') is False or result.get('success') is False)) or re.search(r'<ok>\s*false\s*</ok>|"(?:ok|success)"\s*:\s*false', str(result)):
        return report_tool_failure(name, "service unavailable" if "connection_error" in str(result) else "operation failed")
    return result
