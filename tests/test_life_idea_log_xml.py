from tools.life_idea_log.xml_body import parse_body
from tools.life_idea_log.xml_result import result


def test_parse_body_accepts_flat_xml():
    data, error = parse_body("<action>list</action><workspace_id>alpha</workspace_id>")

    assert error is None
    assert data["action"] == "list"
    assert data["workspace_id"] == "alpha"


def test_parse_body_rejects_nested_xml():
    data, error = parse_body("<entry><title>Nested</title></entry>")

    assert data is None
    assert error["ok"] is False
    assert error["error_code"] == "invalid_xml"


def test_result_escapes_text():
    xml = result({"ok": True, "message": "a < b"})

    assert "a &lt; b" in xml
    assert xml.startswith("<life_idea_log_result>")
