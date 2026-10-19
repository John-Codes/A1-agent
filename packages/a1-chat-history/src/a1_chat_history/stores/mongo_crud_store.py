"""HistoryStore on MongoCRUD: scoped ops via their methods, exact-id lookups via raw collections."""
from mongodb_crud import MongoCRUD
from pymongo import ReturnDocument

from ..models import UpdateChatSessionRequest, now_iso
from ..rows import new_message_row, new_session_row
from ._bridge import AsyncBridge
from ._mongo_ids import eq_filter, msg_filter, object_id

LIMIT = 100000


class MongoCRUDStore:
    def __init__(self, uri, db_name, timeout_ms=2000):
        self._bridge = bridge = AsyncBridge()
        self._crud = bridge.call(
            MongoCRUD.connect(uri, db_name, server_selection_timeout_ms=timeout_ms)
        )
        for name in ("sessions", "messages"):
            bridge.call(self._crud.ensure_tenant_indexes(name))

    def sessions(self, client_id=None, user_id=None, agent_type=None, agent_id=None, workspace_id=None):
        extra = eq_filter(client_id=client_id, user_id=user_id, agent_type=agent_type, agent_id=agent_id)
        if workspace_id:
            return self._call(
                self._crud.find("sessions", workspace_id, filter=extra, limit=LIMIT, sort="-updated_at")
            )
        return self._raw_list("sessions", extra, ("updated_at", -1))

    def create_session(self, item):
        session = new_session_row(item)
        session.pop("id")
        workspace = session.pop("workspace_id")
        new_id = self._call(self._crud.insert_one("sessions", session, workspace_id=workspace))
        return {"id": new_id, "workspace_id": workspace, **session}

    def update_chat_session(self, session_id, item):
        update = {"updated_at": now_iso()}
        if item.title is not None:
            update["title"] = item.title
        if item.summary is not None:
            update["summary"] = item.summary
        doc = self._find_session(session_id)
        if doc is None:
            return None
        query = {"_id": doc["_id"]}
        self._call(self._crud.update_one("sessions", doc["workspace_id"], query, {"$set": update}))
        return self._call(self._crud.find_one("sessions", doc["workspace_id"], query))

    def save_generated_title_and_summary(self, session_id, generated):
        return self.update_chat_session(
            session_id,
            UpdateChatSessionRequest(title=generated.title, summary=generated.summary),
        )

    def delete_session(self, session_id):
        doc = self._find_session(session_id)
        if doc is None:
            return
        self._call(self._crud.delete_one("sessions", doc["workspace_id"], {"_id": doc["_id"]}))
        self._call(self._crud.delete_many("messages", doc["workspace_id"], {"session_id": session_id}))

    def messages(self, session_id, workspace_id=None):
        return self._raw_list("messages", {"session_id": session_id}, ("timestamp", 1))

    def add_message(self, session_id, item):
        doc = self._find_session(session_id) or {}
        message = new_message_row(doc.get("workspace_id", ""), session_id, item)
        message.pop("id")
        workspace = message.pop("workspace_id")
        new_id = self._call(self._crud.insert_one("messages", message, workspace_id=workspace))
        if doc:
            self._call(self._crud.update_one(
                "sessions", doc["workspace_id"], {"_id": doc["_id"]}, {"$set": {"updated_at": now_iso()}}
            ))
        return {"id": new_id, "workspace_id": workspace, **message}

    def delete_message(self, session_id, message_id):
        self._call(self._coll("messages").delete_one(msg_filter(session_id, message_id)))

    def set_feedback(self, session_id, message_id, feedback):
        value = feedback if feedback in ("like", "dislike") else None
        row = self._call(self._coll("messages").find_one_and_update(
            msg_filter(session_id, message_id),
            {"$set": {"feedback": value}},
            return_document=ReturnDocument.AFTER,
        ))
        return MongoCRUD._doc_id(row) if row else None

    def clear_messages(self, session_id):
        self._call(self._coll("messages").delete_many({"session_id": session_id}))

    def _call(self, coro):
        return self._bridge.call(coro)

    def _coll(self, name):
        return self._crud.collection(name)

    def _raw_list(self, name, filter_, order):
        cursor = self._coll(name).find(filter_).sort(*order)
        return [MongoCRUD._doc_id(row) for row in self._call(cursor.to_list(length=LIMIT))]

    def _find_session(self, session_id):
        coll = self._coll("sessions")
        oid = object_id(session_id)

        async def _run():
            if oid is not None:
                doc = await coll.find_one({"_id": oid})
                if doc:
                    return doc
            return await coll.find_one({"id": session_id})

        return self._call(_run())
