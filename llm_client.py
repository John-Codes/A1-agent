from multiprocessing import get_context

from config import LITELLM_ENABLED, LLM_GENERATION_TIMEOUT
from llm_errors import error_result, ok_result
from llm_provider_calls import call_ollama_direct, call_provider
from llm_runtime import active_routes, remember_active
from tools.log import log_exception, log_tool_event


def complete_prompt(prompt, shared):
    attempts = []
    shared["last_llm_error"] = None
    shared["last_llm_attempts"] = []
    shared["last_llm_fallback_used"] = False
    for route in active_routes(shared):
        result = _try_route(prompt, route, shared.get("pending_image_data") or "")
        result["label"] = route["label"]
        attempts.append(result)
        shared["last_llm_attempts"] = attempts
        if result["ok"]:
            remember_active(shared, result)
            shared["last_llm_fallback_used"] = route["label"].startswith("fallback_")
            return result
        shared["last_llm_error"] = result
        log_tool_event("llm", "error", result)
    return attempts[-1] if attempts else error_result("", "", "", RuntimeError("No LLM routes."))


def _try_route(prompt, route, image_data=""):
    ctx = get_context("spawn")
    queue = ctx.Queue()
    process = ctx.Process(target=_route_worker, args=(prompt, route, image_data, queue))
    process.start()
    timeout = min(LLM_GENERATION_TIMEOUT, 60) if route["provider"] == "ollama" else LLM_GENERATION_TIMEOUT
    process.join(timeout)
    if process.is_alive():
        process.terminate()
        process.join(2)
        return error_result(
            route["provider"],
            route["model"],
            route.get("api_base") or "",
            TimeoutError(f"LLM route exceeded {timeout}s"),
        )
    if queue.empty():
        return error_result(
            route["provider"],
            route["model"],
            route.get("api_base") or "",
            RuntimeError("LLM route exited without a result."),
        )
    return queue.get()


def _route_worker(prompt, route, image_data, queue):
    provider = route["provider"]
    model = route["model"]
    api_base = route.get("api_base") or ""
    try:
        if LITELLM_ENABLED:
            text = call_provider(prompt, provider, model, api_base, image_data)
        else:
            text = call_ollama_direct(prompt, model, api_base, image_data)
        queue.put(ok_result(provider, model, api_base, text))
    except Exception as exc:
        log_exception(f"llm.{provider}", exc)
        queue.put(error_result(provider, model, api_base, exc))
