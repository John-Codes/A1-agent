from features.terminal_output.colors import color_enabled, paint
from features.terminal_output.labels import color_for, llm_label
from features.terminal_output.thinking import split_thinking


def render(result, use_color=None):
    if result.get("kind") == "empty":
        return ""
    enabled = color_enabled() if use_color is None else use_color
    if result.get("error"):
        return _line("ERROR", result["error"], enabled)
    lines = []
    if result.get("llm_fallback_used"):
        lines.append(_line("WARNING", "MasterLLM fallback used", enabled))
    lines.append(_main_line(result, enabled))
    return "\n".join(line for line in lines if line)


def input_prompt(use_color=None):
    enabled = color_enabled() if use_color is None else use_color
    return f"{_tag('YOU', enabled)} "


def _main_line(result, enabled):
    kind = result.get("kind")
    if kind == "message":
        return _llm_output(result, enabled)
    if kind == "tick":
        return _line(llm_label(result, "tick"), result.get("response", ""), enabled)
    if kind == "tool":
        return _line("DATA", result.get("response", ""), enabled)
    text = result.get("text", "")
    return _line(_text_category(result, text), text, enabled)


def _llm_output(result, enabled):
    thinking, answer = split_thinking(result.get("response", ""))
    lines = []
    if thinking:
        lines.append(_line(llm_label(result, "thinking"), thinking, enabled))
    if answer or not thinking:
        lines.append(_line(llm_label(result), answer, enabled))
    return "\n".join(lines)


def _text_category(result, text):
    if text.startswith("ERROR |"):
        return "ERROR"
    if result.get("category"):
        return result["category"].upper()
    return "INFO"


def _line(label, text, enabled):
    if label == "ERROR" and str(text).startswith("ERROR |"):
        text = str(text).removeprefix("ERROR |").strip()
    return f"{_tag(label, enabled)} {text}"


def _tag(label, enabled):
    return paint(f"{label}:", color_for(label), enabled)
