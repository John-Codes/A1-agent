from fastapi.testclient import TestClient

from a1_chat_history.app import create_app
from a1_chat_history.settings import Settings
from a1_chat_history.stores import get_store


def make_client(tmp_path, token=""):
    settings = Settings(data_file=str(tmp_path / "history.json"), storage="json", tool_token=token)
    store, backend = get_store(settings)
    assert backend == "json-file"
    return TestClient(create_app(store, token))


def test_full_contract(tmp_path):
    client = make_client(tmp_path)
    assert client.get("/health").json() == {"status": "ok"}

    session = client.post("/sessions", json={
        "workspace_id": "aone-local", "client_id": "A1", "user_id": "local",
        "agent_type": "hermes", "title": "t",
    }).json()
    assert session["workspace_id"] == "aone-local"

    message = client.post(f"/sessions/{session['id']}/messages", json={
        "text": "hello", "mine": True,
    }).json()
    assert message["text"] == "hello"

    listed = client.get(
        "/sessions", params={"client_id": "A1", "agent_type": "hermes"}
    ).json()
    assert listed[0]["id"] == session["id"]

    updated = client.post(
        f"/sessions/{session['id']}/generated-title-and-summary",
        json={"title": "Title", "summary": "Summary"},
    ).json()
    assert updated["title"] == "Title"

    xml = client.post("/tools/chat_history_api", json={
        "body": f"<action>add_message</action><session_id>{session['id']}</session_id>"
        "<text>via xml</text><mine>false</mine>"
    })
    assert xml.status_code == 200 and "<ok>true</ok>" in xml.text
    assert client.get(f"/sessions/{session['id']}/messages").json()[-1]["text"] == "via xml"

    assert client.delete(f"/sessions/{session['id']}").status_code == 204


def test_tool_token_middleware(tmp_path):
    client = make_client(tmp_path, token="secret")
    assert client.get("/health").status_code == 200
    assert client.post("/sessions", json={}).status_code == 401
    ok = client.post(
        "/sessions", json={}, headers={"X-Tool-Token": "secret"}
    )
    assert ok.status_code == 201
