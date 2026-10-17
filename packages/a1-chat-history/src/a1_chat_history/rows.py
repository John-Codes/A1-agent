from uuid import uuid4

from .models import now_iso
from .workspace_ids import clean_workspace_id


def filter_sessions(items, client_id, user_id, agent_type, agent_id, workspace_id):
    if workspace_id is not None:
        workspace_id = clean_workspace_id(workspace_id)
        items = [s for s in items if s.get("workspace_id", "") == workspace_id]
    if client_id:
        items = [s for s in items if s["client_id"] == client_id]
    if user_id:
        items = [s for s in items if s["user_id"] == user_id]
    if agent_type:
        items = [s for s in items if s["agent_type"] == agent_type]
    if agent_id:
        items = [s for s in items if s.get("agent_id") == agent_id]
    return sorted(items, key=lambda s: s["updated_at"], reverse=True)


def new_session_row(item):
    stamp = now_iso()
    return {
        "id": uuid4().hex,
        "workspace_id": item.workspace_id,
        "user_id": item.user_id,
        "client_id": item.client_id,
        "agent_type": item.agent_type,
        "model_name": item.model_name,
        "agent_id": item.agent_id,
        "title": item.title,
        "summary": item.summary,
        "created_at": stamp,
        "updated_at": stamp,
    }


def new_message_row(session_workspace, session_id, item):
    return {
        "id": uuid4().hex,
        "workspace_id": clean_workspace_id(session_workspace),
        "session_id": session_id,
        "text": item.text,
        "mine": item.mine,
        "timestamp": item.timestamp or now_iso(),
        "has_image": item.has_image or item.image_data is not None,
        "feedback": None,
    }


def session_summary(item):
    return {
        "id": item.get("id", ""),
        "title": item.get("title", ""),
        "summary": item.get("summary", ""),
        "updated_at": item.get("updated_at", ""),
    }
