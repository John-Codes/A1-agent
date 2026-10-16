from multiprocessing import get_context
from queue import Empty
from time import monotonic

from config import LITELLM_ENABLED, LLM_GENERATION_TIMEOUT
from llm_errors import error_result, ok_result
from llm_provider_calls import call_ollama_direct, call_provider
from llm_runtime import active_routes, remember_active
from tools.log import log_exception, log_tool_event, report_model_failure


def complete_prompt(prompt, shared):
    attempts = []
    shared["last_llm_error"] = None
    shared["last_llm_attempts"] = []
    shared["last_llm_fallback_used"] = False
    for route in active_routes(shared):
        try:
            result = _try_route(prompt, route, shared.get("pending_image_data") or "")
        except Exception as exc:
            log_exception('llm.' + route['provider'], exc)
            result = error_result(route['provider'], route['model'], route.get('api_base') or '', exc)
        result["label"] = route["label"]
        attempts.append(result)
        shared["last_llm_attempts"] = attempts
        if result["ok"]:
            remember_active(shared, result)
            shared["last_llm_fallback_used"] = route["label"].startswith("fallback_")
            return result
        shared["last_llm_error"] = result
        report_model_failure(route['provider'], route['model'], result.get('error') or {})
        log_tool_event("llm", "error", result)
    return attempts[-1] if attempts else error_result("", "", "", RuntimeError("No LLM routes."))


def _try_route(prompt, route, image_data=""):
    ctx = get_context("spawn")
    queue = ctx.Queue()
    process = ctx.Process(target=_route_worker, args=(prompt, route, image_data, queue))
    process.start()
    timeout = min(LLM_GENERATION_TIMEOUT, 300) if route["provider"] == "ollama" else LLM_GENERATION_TIMEOUT
    deadline = monotonic() + timeout
    try:
        # Drain the queue before joining: a large article can fill the pipe,
        # preventing the child from exiting until the parent reads its result.
        while True:
            remaining = deadline - monotonic()
            if remaining <= 0:
                raise TimeoutError(f"LLM route exceeded {timeout}s")
            try:
                return queue.get(timeout=min(0.2, remaining))
            except Empty:
                if not process.is_alive():
                    raise RuntimeError("LLM route exited without a result.") from None
    except (TimeoutError, RuntimeError) as exc:
        return error_result(route['provider'], route['model'], route.get('api_base') or '', exc)
    finally:
        process.join(0.2)
        if process.is_alive():
            process.terminate()
            process.join(2)
        queue.close()
        queue.join_thread()


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
