from threading import Lock

from config import LOG_PATH, MEMORY_PATH
from chat_history_auto_save import save_user_message_before_generation
from nodes import LLMNode
from rag_sync import sync_if_stale
from store import store
from tools import dispatch_tool_call

_lock = Lock()
_llm = LLMNode()


def message(text, chat_history_session_id="", user_message="", image_data="", on_chunk=None):
    sync_if_stale(background=True)
    with _lock:
        store["trigger"] = "message"
        store["pending_input"] = text
        store["pending_image_data"] = image_data
        if on_chunk is not None:
            store["stream_callback"] = on_chunk
            store["streamed"] = True
        if chat_history_session_id:
            store["chat_history_session_id"] = chat_history_session_id
        save_user_message_before_generation(store, user_message or text)
        _llm.run(store)
        return _result()


def tick():
    from heartbeat.service import service
    return service.tick()


def tool(name, body=""):
    with _lock:
        return dispatch_tool_call({"name": name, "body": body})


def memory():
    return MEMORY_PATH.read_text(encoding="utf-8") if MEMORY_PATH.exists() else ""


def log():
    return LOG_PATH.read_text(encoding="utf-8") if LOG_PATH.exists() else ""


def _result():
    result = {
        "speaker": "master_llm",
        "response": store.get("pending_response") or "",
        "streamed": bool(store.get("streamed")),
        "streamed_chunks": len(store.get("pending_stream") or []),
        "error": store.get("last_error"),
        "llm_error": store.get("last_llm_error"),
        "llm_attempts": store.get("last_llm_attempts", []),
        "llm_fallback_used": store.get("last_llm_fallback_used", False),
        "embedding_error": store.get("last_embedding_error"),
        "embedding_attempts": store.get("last_embedding_attempts", []),
    }
    store["stream_callback"] = None
    store["streamed"] = False
    store["pending_stream"] = []
    return result
