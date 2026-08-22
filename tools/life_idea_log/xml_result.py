from xml.sax.saxutils import escape


def result(data):
    return "<life_idea_log_result>\n" + _nodes(data) + "</life_idea_log_result>"


def _nodes(data):
    if isinstance(data, dict):
        return "".join(_tag(key, value) for key, value in data.items())
    return _tag("message", data)


def _tag(key, value):
    if isinstance(value, dict):
        return f"  <{key}>\n{_nodes(value)}  </{key}>\n"
    if isinstance(value, list):
        return f"  <{key}>\n{''.join(_tag('item', item) for item in value)}  </{key}>\n"
    if isinstance(value, bool):
        text = "true" if value else "false"
    else:
        text = "" if value is None else escape(str(value))
    return f"  <{key}>{text}</{key}>\n"
