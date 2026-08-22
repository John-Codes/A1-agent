import asyncio

from config import (
    LLM_GENERATION_TIMEOUT,
    BROWSER_USE_CHROMIUM_SANDBOX,
    BROWSER_USE_OLLAMA_MODEL,
    BROWSER_USE_TIMEOUT,
    BROWSER_USE_CHROMIUM_EXECUTABLE,
    OLLAMA_HOST,
)
from tools.browser_use_tool.schema import parse_browser_request

SAFETY_NOTE = """

Safety rule: browse, inspect, click, and type as needed, but stop and report
before purchases, form submissions, logins, sending messages, account changes,
or other sensitive irreversible actions.
""".strip()


def run_browser_use(body):
    request = parse_browser_request(body)
    return asyncio.run(_run(request))


async def _run(request):
    from browser_use import Agent, Browser, ChatOllama

    browser = Browser(**_browser_options(request))
    try:
        agent = Agent(
            task=f"{request['task']}\n\n{SAFETY_NOTE}",
            browser=browser,
            llm=ChatOllama(model=BROWSER_USE_OLLAMA_MODEL, host=OLLAMA_HOST, timeout=LLM_GENERATION_TIMEOUT),
            llm_timeout=LLM_GENERATION_TIMEOUT,
            step_timeout=LLM_GENERATION_TIMEOUT,
        )
        result = await asyncio.wait_for(
            agent.run(max_steps=request["max_steps"]),
            timeout=BROWSER_USE_TIMEOUT,
        )
        return _stringify_result(result)
    finally:
        await _close_browser(browser)


def _browser_options(request):
    options = {
        "headless": True,  # Force headless for Jetson/ARM64 reliability
        "chromium_sandbox": BROWSER_USE_CHROMIUM_SANDBOX,
        "window_size": {"width": 1280, "height": 900},
    }
    if BROWSER_USE_CHROMIUM_EXECUTABLE:
        options["executable_path"] = BROWSER_USE_CHROMIUM_EXECUTABLE
    if request["allowed_domains"]:
        options["allowed_domains"] = request["allowed_domains"]
    return options


async def _close_browser(browser):
    close = getattr(browser, "close", None) or getattr(browser, "stop", None)
    if close:
        result = close()
        if asyncio.iscoroutine(result):
            await result


def _stringify_result(result):
    final_result = getattr(result, "final_result", None)
    if callable(final_result):
        final = final_result()
        if final:
            return str(final)
    return str(result)
