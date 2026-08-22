import os
import sys


COLORS = {
    "blue": "\033[34m",
    "cyan": "\033[36m",
    "green": "\033[32m",
    "magenta": "\033[35m",
    "red": "\033[31m",
    "yellow": "\033[33m",
}
RESET = "\033[0m"


def color_enabled(stream=None, environ=None):
    stream = sys.stdout if stream is None else stream
    environ = os.environ if environ is None else environ
    return "NO_COLOR" not in environ and bool(getattr(stream, "isatty", lambda: False)())


def paint(text, color, enabled):
    if not enabled:
        return text
    return f"{COLORS[color]}{text}{RESET}"
