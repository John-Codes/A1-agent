import sys

from features.terminal_output.colors import RESET, color_enabled, paint

DIM = "\033[2m"


def live_printer(stream=None):
    """Build an on_chunk callback that prints thinking/content tokens live.

    Option A UX: stream everything as it arrives; on {"type": "reset"} close
    the current line; on {"type": "tool_status"} show a tool line.
    """
    out = sys.stdout if stream is None else stream
    enabled = color_enabled(out)
    state = {"open": False, "last": None}

    def _newline():
        if state["open"]:
            out.write("\n")
            state["open"] = False

    def printer(item):
        kind = item.get("type")
        if kind == "reset":
            _newline()
            state["last"] = None
            return
        if kind == "tool_status":
            _newline()
            out.write(paint(f"· {item.get('name', 'tool')} …", "cyan", enabled))
            out.write("\n")
            out.flush()
            return
        if kind != "chunk":
            return
        text = item.get("text", "")
        chunk_kind = item.get("kind")
        if chunk_kind == "thinking":
            if state["last"] == "content":
                _newline()
            out.write(f"{DIM}{text}{RESET}" if enabled else text)
        else:
            if state["last"] == "thinking":
                _newline()
            out.write(text)
        state["open"] = True
        state["last"] = chunk_kind
        out.flush()

    return printer
