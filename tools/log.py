from datetime import datetime
import os
import re
import traceback

from config import LOG_PATH


def log_tool_event(name, status, detail):
    _write(f"{_stamp()} | TOOL | {name}:{status} | {detail}")


def log_exception(name, exc):
    detail = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"
    message = f"{_stamp()} | ERROR | {name} | {detail}"
    _write(message)


def _write(message):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(f"{redact(message)}\n")


def _stamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def redact(text):
    text = str(text)
    text = re.sub(r"(<(?:api_key|token|password|secret)>).*?(</(?:api_key|token|password|secret)>)", r"\1[REDACTED]\2", text, flags=re.I | re.S)
    for name, value in os.environ.items():
        if any(word in name.upper() for word in ("KEY", "TOKEN", "SECRET", "PASSWORD")) and len(value) >= 8:
            text = text.replace(value, "[REDACTED]")
    return text


def brief_error(name, detail):
    text = str(detail).lower()
    if "403" in text or "401" in text:
        reason = "access denied; check the API key or permissions"
    elif "connection refused" in text or "connection_error" in text:
        reason = "service unavailable"
    elif isinstance(detail, TimeoutError) or "timeout" in text or "timed out" in text:
        reason = "request timed out"
    elif "llm failed" in text:
        reason = "all LLM routes failed"
    elif "browser task did not complete" in text:
        reason = "browser task did not complete"
    else:
        reason = " ".join((str(detail).splitlines() or ["operation failed"])[0].split())[:160] or "operation failed"
    return redact(f"Tool {name} failed: {reason}. Check log for more info @ {LOG_PATH.resolve()}")


def report_model_failure(provider, model, error):
    reason = error.get('message', 'No response') if isinstance(error, dict) else str(error)
    reason = ' '.join(reason.split())[:200] or type(error).__name__
    from features.terminal_output.status import decorate
    message = redact(f"MODEL FAILED | {provider}/{model}: {reason}. "
                     f"Check log for more info @ {LOG_PATH.resolve()}")
    print(decorate(message), flush=True)


def report_tool_failure(name, detail):
    from features.terminal_output.status import decorate
    message = brief_error(name, detail)
    print(decorate(message), flush=True)
    return message
