from xml.etree import ElementTree as ET


def parse_body(body):
    try:
        root = ET.fromstring(f"<root>{body or ''}</root>")
    except ET.ParseError as exc:
        return None, error("invalid_xml", str(exc))
    data = {}
    for child in root:
        if list(child):
            return None, error("invalid_xml", f"Nested tag not allowed: {child.tag}")
        data[child.tag.strip()] = (child.text or "").strip()
    return data, None


def error(code, message):
    return {"ok": False, "error_code": code, "message": message}
