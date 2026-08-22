from xml.sax.saxutils import escape

from tools.chat_history.client import ChatHistoryClient


def run_chat_history_api(body):
    response = ChatHistoryClient().post("/tools/chat_history_api", {"body": body})
    if not response.get("ok"):
        return _remote_error(response)
    return str(response.get("body") or "")


def _remote_error(response):
    code = response.get("error_code") or response.get("status_code") or "remote_error"
    body = escape(str(response.get("body") or "chat history tool request failed"))
    return (
        "<chat_history_result>\n"
        "  <ok>false</ok>\n"
        f"  <error_code>{escape(str(code))}</error_code>\n"
        f"  <body>{body}</body>\n"
        "</chat_history_result>"
    )
