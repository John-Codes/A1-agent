from pymongo import ReturnDocument

from ..models import UpdateChatSessionRequest, now_iso
from ..rows import new_message_row, new_session_row


class MongoStore:
    """pymongo-backed history store. Requires `pip install a1-chat-history[mongo]`."""

    def __init__(self, uri, db_name, timeout_ms=2000):
        from pymongo import MongoClient

        self._client = MongoClient(uri, serverSelectionTimeoutMS=timeout_ms)
        self._db = self._client[db_name]
        self._sessions = self._db["sessions"]
        self._messages = self._db["messages"]
        self._client.admin.command("ping")

    @staticmethod
    def _clean(row):
        if row is None:
            return None
        row.pop("_id", None)
        return row

    def sessions(self, client_id=None, user_id=None, agent_type=None, agent_id=None, workspace_id=None):
        query = {}
        for key, value in {
            "client_id": client_id, "user_id": user_id,
            "agent_type": agent_type, "agent_id": agent_id, "workspace_id": workspace_id,
        }.items():
            if value:
                query[key] = value
        rows = self._sessions.find(query).sort("updated_at", -1)
        return [self._clean(row) for row in rows]

    def create_session(self, item):
        session = new_session_row(item)
        self._sessions.insert_one(dict(session))
        return session

    def update_chat_session(self, session_id, item):
        update = {"updated_at": now_iso()}
        if item.title is not None:
            update["title"] = item.title
        if item.summary is not None:
            update["summary"] = item.summary
        row = self._sessions.find_one_and_update(
            {"id": session_id}, {"$set": update}, return_document=ReturnDocument.AFTER
        )
        return self._clean(row)

    def save_generated_title_and_summary(self, session_id, generated):
        return self.update_chat_session(
            session_id,
            UpdateChatSessionRequest(title=generated.title, summary=generated.summary),
        )

    def delete_session(self, session_id):
        self._sessions.delete_one({"id": session_id})
        self._messages.delete_many({"session_id": session_id})

    def messages(self, session_id, workspace_id=None):
        rows = self._messages.find({"session_id": session_id}).sort("timestamp", 1)
        return [self._clean(row) for row in rows]

    def add_message(self, session_id, item):
        session = self._sessions.find_one({"id": session_id}) or {}
        message = new_message_row(session.get("workspace_id", ""), session_id, item)
        self._messages.insert_one(dict(message))
        self._sessions.update_one(
            {"id": session_id}, {"$set": {"updated_at": now_iso()}}
        )
        return message

    def delete_message(self, session_id, message_id):
        self._messages.delete_one({"session_id": session_id, "id": message_id})

    def set_feedback(self, session_id, message_id, feedback):
        value = feedback if feedback in ("like", "dislike") else None
        row = self._messages.find_one_and_update(
            {"session_id": session_id, "id": message_id},
            {"$set": {"feedback": value}},
            return_document=ReturnDocument.AFTER,
        )
        return self._clean(row)

    def clear_messages(self, session_id):
        self._messages.delete_many({"session_id": session_id})
