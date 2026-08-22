import agent
from embedding_commands import run_embedding_command
from llm_commands import run_llm_command
from tools import tool_names

EXIT_COMMANDS = {"/quit", "/exit", "/q"}


def run(text):
    text = (text or "").strip()
    if not text:
        return {"kind": "empty", "text": ""}

    command, body = _split(text)
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
