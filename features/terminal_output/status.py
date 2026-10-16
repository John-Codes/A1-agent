import re

from features.terminal_output.colors import RESET, color_enabled, paint

# Bright ANSI color codes (91-96) vs normal (31-35)
BRIGHT = {
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "MAGENTA": "\033[95m",
    "CYAN": "\033[96m",
    "WHITE": "\033[97m",
}
NORMAL = {
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "BLUE": "\033[34m",
    "MAGENTA": "\033[35m",
    "CYAN": "\033[36m",
    "WHITE": "\033[37m",
}

TONES = {
    "BLOCKED": "YELLOW",
    "DONE": "GREEN",
    "ERROR": "RED",
    "EXECUTE": "CYAN",
    "FAILED": "RED",
    "HEARTBEAT": "BLUE",
    "INFO": "BLUE",
    "INTERRUPTED": "YELLOW",
    "MODEL FAILED": "RED",
    "PAUSED": "YELLOW",
    "PLAN": "CYAN",
    "RUNNING": "CYAN",
    "SEO": "GREEN",
    "SEO MAIL": "GREEN",
    "STOPPED": "RED",
    "SUCCESS": "GREEN",
    "WARNING": "YELLOW",
}

_URL = re.compile(r"https?://[^\s]+")
_PATH = re.compile(r"(?<![\w/])(?:/[\w.~-]+){2,}")
_COMMAND = re.compile(r"(?<![\w/])/[a-z][a-z0-9_-]*")
_NUMBER = re.compile(r"\b\d+\b")
_STATUS = re.compile(r"\b(done|failed|error|stopped|paused|blocked|interrupted|running|pending|scheduled)\b", re.I)

_RULES = (
    (_URL, "\033[1;94m"),
    (_PATH, "\033[1;96m"),
    (_COMMAND, "\033[1;96m"),
    (_STATUS, None),
    (_NUMBER, "\033[1;93m"),
)

_STATUS_COLOR = {
    "done": "GREEN",
    "failed": "RED",
    "error": "RED",
    "stopped": "RED",
    "paused": "YELLOW",
    "blocked": "YELLOW",
    "interrupted": "YELLOW",
    "running": "CYAN",
    "pending": "BLUE",
    "scheduled": "BLUE",
}


def emit(label, text, tone=None):
    print(status_line(label, text, tone), flush=True)


def status_line(label, text, tone=None, enabled=None):
    enabled = color_enabled() if enabled is None else enabled
    label = str(label)
    body = "" if text is None else str(text)
    if not enabled:
        return f"{label} | {body}"
    color_key = tone or TONES.get(label, "BLUE")
    color_code = BRIGHT.get(color_key, NORMAL.get(color_key, ""))
    return f"{paint(label + ' |', color_key, True)} {highlight(body, True)}"


def decorate(text, enabled=None):
    enabled = color_enabled() if enabled is None else enabled
    text = "" if text is None else str(text)
    if not enabled:
        return text
    return "\n".join(_decorate_line(line) for line in text.splitlines())


def highlight(text, enabled):
    text = "" if text is None else str(text)
    if not enabled or not text:
        return text
    pieces = []
    index = 0
    while index < len(text):
        best = None
        for pattern, style in _RULES:
            match = pattern.search(text, index)
            if not match:
                continue
            if best is None or match.start() < best[0] or (match.start() == best[0] and match.end() > best[1]):
                best = (match.start(), match.end(), style, match.group(0))
        if best is None:
            pieces.append(text[index:])
            break
        start, end, style, token = best
        pieces.append(text[index:start])
        pieces.append(_paint_token(token, style))
        index = end
    return "".join(pieces)


def _decorate_line(line):
    match = _PREFIX.match(line)
    if match and match.group("label") in TONES:
        return status_line(match.group("label"), match.group("body"), enabled=True)
    return highlight(line, True)


def _paint_token(token, style):
    if style is None:
        return paint(token, _STATUS_COLOR.get(token.lower(), "BLUE"), True)
    return f"{style}{token}{RESET}"
