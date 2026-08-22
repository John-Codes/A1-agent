from xml.sax.saxutils import escape

from tools.trello_clone.client import TrelloCloneClient

TOOL_PATH = "/tools/trello_clone_agent_friendly_xml"


def run_trello_clone_agent_friendly_xml(body):
    response = TrelloCloneClient().post(TOOL_PATH, {"body": body})
    if isinstance(response, str):
        return response
    if response.get("ok") is False:
        return remote_error(response)
    return str(response.get("body") or "")


def remote_error(response):
    code = response.get("error_code") or response.get("status_code") or "remote_error"
    body = response.get("body") or "trello clone XML tool request failed"
    return (
        "<trello_clone_result>\n"
        "  <ok>false</ok>\n"
        f"  <error_code>{escape(str(code))}</error_code>\n"
        f"  <body>{escape(str(body))}</body>\n"
        "</trello_clone_result>"
    )
