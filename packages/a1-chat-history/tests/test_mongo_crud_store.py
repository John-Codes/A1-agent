"""Integration tests against the live MongoDB on 127.0.0.1:27017 (skipped when absent)."""
import pytest

from a1_chat_history.models import MessageIn, SessionIn, UpdateChatSessionRequest
from a1_chat_history.mongo_runtime import mongo_reachable
from a1_chat_history.stores.mongo_crud_store import MongoCRUDStore

URI = "mongodb://127.0.0.1:27017"
DB = "a1_chat_history_test"

pytestmark = pytest.mark.skipif(
    not mongo_reachable(URI, 1500), reason=f"no MongoDB at {URI}"
)


@pytest.fixture
def store():
    s = MongoCRUDStore(URI, DB, timeout_ms=1500)
    _wipe(s)
    yield s
    _wipe(s)


def _wipe(s):
    for name in ("sessions", "messages"):
        s._call(s._coll(name).delete_many({}))


def _session(store, workspace="ws-a", **kw):
    return store.create_session(SessionIn(workspace_id=workspace, client_id="A1", **kw))


def test_round_trip(store):
    session = _session(store, title="first")
    assert len(session["id"]) == 24 and session["workspace_id"] == "ws-a"

    message = store.add_message(session["id"], MessageIn(text="hello", mine=True))
    assert message["text"] == "hello" and message["workspace_id"] == "ws-a"
    assert store.messages(session["id"])[0]["text"] == "hello"

    assert store.sessions(workspace_id="ws-a")[0]["id"] == session["id"]
    assert store.update_chat_session(session["id"], UpdateChatSessionRequest(title="T"))["title"] == "T"
    assert store.update_chat_session("missing", UpdateChatSessionRequest(title="x")) is None

    updated = store.set_feedback(session["id"], message["id"], "like")
    assert updated["feedback"] == "like"
    assert store.set_feedback(session["id"], "nope", "like") is None

    store.delete_message(session["id"], message["id"])
    assert store.messages(session["id"]) == []
    store.delete_session(session["id"])
    assert store.sessions(workspace_id="ws-a") == []


def test_tenant_isolation(store):
    a = _session(store, workspace="ws-a")
    b = _session(store, workspace="ws-b")
    assert [s["id"] for s in store.sessions(workspace_id="ws-a")] == [a["id"]]
    assert [s["id"] for s in store.sessions(workspace_id="ws-b")] == [b["id"]]
    assert {s["id"] for s in store.sessions()} == {a["id"], b["id"]}
