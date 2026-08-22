from datetime import datetime
import traceback

from config import LOG_PATH


def log_tool_event(name, status, detail):
    message = f"{_stamp()} | TOOL | {name}:{status} | {_clean(detail)}"
    print(message)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(f"{message}\n")


def log_exception(name, exc):
    detail = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"
    message = f"{_stamp()} | ERROR | {name} | {detail}"
    print(message)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(f"{message}\n")


def _stamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _clean(text):
    return " ".join(str(text).split())[:500]
