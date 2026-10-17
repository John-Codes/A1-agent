import xml.etree.ElementTree as ET

from a1_chat_history.stores.json_store import JsonStore
from a1_chat_history.xml_tool import run_chat_history_xml_action


def _tag_value(xml_text, tag):
    root = ET.fromstring(xml_text)
    node = root.find(f".//{tag}")
    return node.text if node is not None else None


def test_create_and_add_via_xml(tmp_path):
    store = JsonStore(tmp_path / "history.json")
    created = run_chat_history_xml_action(
        store,
        "<action>create_session</action><workspace_id>aone-local</workspace_id>"
        "<client_id>A1</client_id><user_id>local</user_id><agent_type>hermes</agent_type>"
        "<title>t</title><summary></summary>",
    )
    assert _tag_value(created, "ok") == "true"
    session_id = _tag_value(created, "id")
    assert session_id

    added = run_chat_history_xml_action(
        store,
        f"<action>add_message</action><session_id>{session_id}</session_id>"
        "<text>hello world</text><mine>true</mine>",
    )
    assert _tag_value(added, "ok") == "true"

    listed = run_chat_history_xml_action(
        store, f"<action>list_messages</action><session_id>{session_id}</session_id>"
    )
    assert _tag_value(listed, "text") == "hello world"


def test_missing_tag_and_unknown_action(tmp_path):
    store = JsonStore(tmp_path / "history.json")
    missing = run_chat_history_xml_action(store, "<action>add_message</action>")
    assert _tag_value(missing, "error_code") == "missing_required_tag"
    unknown = run_chat_history_xml_action(store, "<action>bogus</action>")
    assert _tag_value(unknown, "error_code") == "unknown_action"
    broken = run_chat_history_xml_action(store, "<action><bad")
    assert _tag_value(broken, "error_code") == "invalid_xml"
