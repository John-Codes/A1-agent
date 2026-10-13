"""Deterministic reviewer-mail polling for the CDL SEO workflow."""
import json
import re
from pathlib import Path

from config import AGENTMAIL_API_KEY, ROOT_DIR
from tools.agentmail.client import AgentMailClient
from tools.seo_registry import run_seo_registry

INBOX = "gateway-local@agentmail.to"
ALLOW = {"efexzium@gmail.com", "franyr960@gmail.com"}
STATE = ROOT_DIR / ".a1-seo-mail.json"


def poll():
    if not AGENTMAIL_API_KEY:
        return {"processed": 0, "reason": "mail is not configured"}
    client = AgentMailClient()
    state = _load()
    processed = 0
    for row in client.list_messages(INBOX, {"limit": 50, "ascending": False}).get("messages", []):
        if "received" not in row.get("labels", []) or "unread" not in row.get("labels", []):
            continue
        mid = row.get("message_id")
        if not mid or mid in state:
            continue
        sender = _address(row.get("from", ""))
        if sender not in ALLOW:
            continue
        message = client.get_message(INBOX, mid)
        text = (message.get("extracted_text") or message.get("text") or "").lower()
        if "keyword" in text or "palabra clave" in text:
            client.reply(INBOX, mid, {"text": _keyword_reply(), "reply_all": True,
                                      "headers": {"X-A1-Workflow": "cdl-seo-review"}})
        state[mid] = True
        client.update_message(INBOX, mid, {"add_labels": ["read"], "remove_labels": ["unread"]})
        processed += 1
    _save(state)
    return {"processed": processed}


def _keyword_reply():
    rows = run_seo_registry('{"action":"list"}', "cdl_keywords")
    relevant = [line for line in rows.splitlines() if "air brakes" in line.lower() or "frenos de aire" in line.lower()]
    return "Here are the active air-brakes keyword rows from CDL_SEO_KEYWORDS.md:\n\n" + "\n".join(relevant) + "\n\nReply with additions or edits and A1 will update the registry."


def _address(value):
    match = re.search(r"<([^>]+)>$", value)
    return (match.group(1) if match else value).strip().lower()


def _load():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _save(data):
    STATE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
