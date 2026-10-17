from a1_chat_history.models import (
    GeneratedTitleAndSummary,
    MessageIn,
    SessionIn,
    UpdateChatSessionRequest,
)
from a1_chat_history.stores.json_store import JsonStore


def make_store(tmp_path):
    return JsonStore(tmp_path / "history.json")


def test_session_and_message_lifecycle(tmp_path):
    store = make_store(tmp_path)
    session = store.create_session(SessionIn(client_id="A1", agent_type="hermes", title="t"))
    assert session["client_id"] == "A1"

    message = store.add_message(session["id"], MessageIn(text="hello", mine=True))
    assert message["workspace_id"] == session["workspace_id"]
    assert message["has_image"] is False

    store.add_message(session["id"], MessageIn(text="hi back", mine=False))
    assert len(store.messages(session["id"])) == 2

    sessions = store.sessions(client_id="A1")
    assert sessions[0]["id"] == session["id"]


def test_update_delete_and_feedback(tmp_path):
    store = make_store(tmp_path)
    session = store.create_session(SessionIn())
    updated = store.update_chat_session(
        session["id"], UpdateChatSessionRequest(title="new", summary="sum")
    )
    assert updated["title"] == "new"
    assert store.update_chat_session("missing", UpdateChatSessionRequest()) is None

    message = store.add_message(session["id"], MessageIn(text="x", mine=True))
    assert store.set_feedback(session["id"], message["id"], "like")["feedback"] == "like"
    assert store.set_feedback(session["id"], message["id"], "nope")["feedback"] is None

    store.clear_messages(session["id"])
    assert store.messages(session["id"]) == []
    store.delete_session(session["id"])
    assert store.sessions() == []


def test_generated_title_and_summary(tmp_path):
    store = make_store(tmp_path)
    session = store.create_session(SessionIn())
    saved = store.save_generated_title_and_summary(
        session["id"], GeneratedTitleAndSummary(title="T", summary="S")
    )
    assert saved["title"] == "T" and saved["summary"] == "S"
