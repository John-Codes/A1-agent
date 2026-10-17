import json
import os
import threading
from pathlib import Path

from ..models import MessageIn, SessionIn, UpdateChatSessionRequest, now_iso
from ..rows import filter_sessions, new_message_row, new_session_row


class JsonStore:
    """Zero-dependency file-backed history store. Same contract as MongoStore."""

    def __init__(self, path):
        self.path = Path(path).expanduser()
        self._lock = threading.Lock()

    def sessions(self, client_id=None, user_id=None, agent_type=None, agent_id=None, workspace_id=None):
        with self._lock:
            data = self._read()
        return filter_sessions(data["sessions"], client_id, user_id, agent_type, agent_id, workspace_id)

    def create_session(self, item: SessionIn):
        with self._lock:
            data = self._read()
            session = new_session_row(item)
            data["sessions"].append(session)
            self._write(data)
        return session

    def update_chat_session(self, session_id, item: UpdateChatSessionRequest):
        with self._lock:
            data = self._read()
            for session in data["sessions"]:
                if session["id"] == session_id:
                    if item.title is not None:
                        session["title"] = item.title
                    if item.summary is not None:
                        session["summary"] = item.summary
                    session["updated_at"] = now_iso()
                    self._write(data)
                    return session
        return None

    def save_generated_title_and_summary(self, session_id, generated):
        return self.update_chat_session(
            session_id,
            UpdateChatSessionRequest(title=generated.title, summary=generated.summary),
        )

    def delete_session(self, session_id):
        with self._lock:
            data = self._read()
            data["sessions"] = [s for s in data["sessions"] if s["id"] != session_id]
            data["messages"] = [m for m in data["messages"] if m["session_id"] != session_id]
            self._write(data)

    def messages(self, session_id, workspace_id=None):
        with self._lock:
            data = self._read()
        return [m for m in data["messages"] if m["session_id"] == session_id]

    def add_message(self, session_id, item: MessageIn):
        with self._lock:
            data = self._read()
            message = new_message_row(self._session_workspace(data, session_id), session_id, item)
            data["messages"].append(message)
            for session in data["sessions"]:
                if session["id"] == session_id:
                    session["updated_at"] = now_iso()
            self._write(data)
        return message

    def delete_message(self, session_id, message_id):
        with self._lock:
            data = self._read()
            data["messages"] = [
                m for m in data["messages"]
                if not (m["session_id"] == session_id and m["id"] == message_id)
            ]
            self._write(data)

    def set_feedback(self, session_id, message_id, feedback):
        with self._lock:
            data = self._read()
            for message in data["messages"]:
                if message["session_id"] == session_id and message["id"] == message_id:
                    message["feedback"] = feedback if feedback in ("like", "dislike") else None
                    self._write(data)
                    return message
        return None

    def clear_messages(self, session_id):
        with self._lock:
            data = self._read()
            data["messages"] = [m for m in data["messages"] if m["session_id"] != session_id]
            self._write(data)

    def _session_workspace(self, data, session_id):
        for session in data["sessions"]:
            if session["id"] == session_id:
                return session.get("workspace_id")
        return ""

    def _read(self):
        if not self.path.exists():
            return {"sessions": [], "messages": []}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        os.replace(tmp, self.path)
