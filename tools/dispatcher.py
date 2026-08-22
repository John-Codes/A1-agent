import re

from config import MEMORY_PATH
from conversation_history import run_conversation_history
from life_log import run_life_log
from memory import memory_ingest_path, memory_search, memory_store
from rag_sync import run_rag_sync
from tools.agentmail import run_agentmail
from tools.browser_use_tool import run_browser_use
from tools.chat_history import run_chat_history_api
from tools.log import log_exception, log_tool_event
from tools.life_idea_log import run_life_idea_log
from tools.llm_route_config import run_llm_route_config
from tools.shell import run_shell
from tools.trello_clone import run_trello_clone
from tools.trello_clone_agent_friendly_xml import run_trello_clone_agent_friendly_xml
from tools.web import run_web_search

TOOL_RE = re.compile(
    r"<tool\s+name=[\"'](?P<name>[^\"']+)[\"']\s*>(?P<body>.*?)</tool>",
    re.DOTALL,
)

TOOL_HANDLERS = {
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
    name = call["name"]
    body = call["body"]
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
        result = f"{name} error: {exc}"
        log_exception(name, exc)
        return result


def _logged_result(name, result):
    log_tool_event(name, "done", result)
    return result
