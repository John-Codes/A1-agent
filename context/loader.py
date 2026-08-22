import requests

from config import CHAT_HISTORY_API_TOKEN, CHAT_HISTORY_API_URL, CHAT_HISTORY_TIMEOUT, TOOLS_PATH
from rag_sync import retrieve


def load_context_prompt(query=""):
    tools = _read_tools()
    prompt = (
        "## Bootstrap\n"
        "Use retrieved context as the source of truth. You may request tools "
        "with XML tags like <tool name=\"web_search\">query</tool>. Use "
        "rag_sync when context or Trello knowledge may need refreshing."
        f"\n\n## Available Tools\n{tools}"
    )
    if not query:
        return prompt
    return f"{prompt}\n\n## Retrieved Context\n{retrieve(query, 6)}"


def _read_tools():
    if not TOOLS_PATH.exists():
        tools = "(tool catalog unavailable)"
    else:
        tools = TOOLS_PATH.read_text(encoding="utf-8").strip()
    return f"{tools}\n\n{_chat_history_tool_catalog()}".strip()


def _chat_history_tool_catalog():
    try:
        response = requests.get(
            f"{CHAT_HISTORY_API_URL.rstrip('/')}/tools/chat_history_api",
            headers=_chat_history_headers(),
            timeout=CHAT_HISTORY_TIMEOUT,
        )
        response.raise_for_status()
        instructions = response.json().get("instructions", "").strip()
    except requests.RequestException:
        instructions = ""
    except ValueError:
        instructions = ""
    if instructions:
        return "Remote chat history tool catalog:\n" + instructions
    return (
        "Remote chat history tool catalog unavailable. "
        "Tool name remains chat_history_api."
    )


def _chat_history_headers():
    return {"X-Tool-Token": CHAT_HISTORY_API_TOKEN} if CHAT_HISTORY_API_TOKEN else {}
