from features.terminal_markdown.render import model_section
from features.terminal_output.banner import tool_block, tools_panel
from features.terminal_output.colors import color_enabled, paint
from features.terminal_output.labels import color_for, llm_label
from features.terminal_output.status import highlight
from features.terminal_output.thinking import split_thinking


def render(result, use_color=None):
    if result.get("kind") == "empty":
        return ""
    enabled = color_enabled() if use_color is None else use_color
    if result.get("kind") == "display" and result.get("panel") == "tools":
        from tools import tool_names
        return tools_panel(tool_names(), enabled)
    if result.get("error"):
        return _line("ERROR", result["error"], enabled)
    lines = []
    if result.get("llm_fallback_used"):
        lines.append(_line("WARNING", "MasterLLM fallback used", enabled))
    lines.append(_main_line(result, enabled))
    return "\n".join(line for line in lines if line)


def input_prompt(use_color=None):
    enabled = color_enabled() if use_color is None else use_color
    if not enabled:
        return "YOU: "
    return "\033[1;32mYOU\033[0m \033[2m›\033[0m "


def _main_line(result, enabled):
    kind = result.get("kind")
    if kind == "message":
        return _llm_output(result, enabled)
    if kind == "tick":
        return _model_line(llm_label(result, "tick"), result.get("response", ""), enabled)
    if kind == "tool":
        block = tool_block(result.get("name"), result.get("response", ""), enabled)
        return block if block is not None else _line("DATA", result.get("response", ""), enabled)
    text = result.get("text", "")
    return _line(_text_category(result, text), text, enabled)


def _llm_output(result, enabled):
    thinking, answer = split_thinking(result.get("response", ""))
    lines = []
    if thinking:
        lines.append(_model_line(llm_label(result, "thinking"), thinking, enabled, muted=True))
    if answer or not thinking:
        lines.append(_model_line(llm_label(result), answer, enabled))
    return "\n".join(lines)


def _model_line(label, text, enabled, muted=False):
    if "thinking" in label.lower():
        # Display thinking in dim cyan
        body = highlight(text, enabled)
        if enabled:
            return f"{highlight(label, True)} {body}"
        return f"{label}: {body}"
    formatted = model_section(label, text, enabled, color_for(label), muted)
    return formatted if formatted is not None else _line(label, text, enabled, muted=muted)


def _text_category(result, text):
    if text.startswith("ERROR |"):
        return "ERROR"
    if result.get("category"):
        return result["category"].upper()
    return "INFO"


def _line(label, text, enabled, muted=False):
    if label == "ERROR" and str(text).startswith("ERROR |"):
        text = str(text).removeprefix("ERROR |").strip()
    body = highlight(text, enabled)
    if enabled and muted:
        body = f"\033[2;3m{body}\033[0m"
    return f"{_tag(label, enabled)} {body}"


def _tag(label, enabled):
    return paint(f"{label}:", color_for(label), enabled)
