from commands import run as run_command
from task_runtime.controller import command as task_command
from task_runtime.state import PATH
from store import store
from features.terminal_output import render
from features.terminal_output.status import decorate
from features.terminal_output.stream import live_printer
from heartbeat.service import service
from heartbeat.console import read_input


def main():
    from seo.service import service as seo_service
    service.start()
    seo_service.start()
    try:
        _loop()
    finally:
        seo_service.close()
        service.close()


def _loop():
    from seo.service import HELP
    from tools import tool_names
    from features.terminal_output.banner import startup
    print(startup(tool_names(), HELP))
    if PATH.exists():
        store["mode"] = "plan"
    while True:
        text = _read()
        if text.strip() == '/tick':
            _show(service.request())
            continue
        if text.split(maxsplit=1)[:1] == ['/heartbeat']:
            action = text.partition(' ')[2].strip()
            if action == 'resume':
                _show(service.resume())
            elif action == 'stop':
                service.stop()
                _show("Heartbeat paused.")
            else:
                _show(service.status())
            continue
        task_result = task_command(text.strip())
        if task_result is not None:
            store["mode"] = "plan"
            _show(task_result)
            if text.strip() == '/status':
                _show(service.status())
            continue
        if store.get("mode") == "plan" and text.strip() and not text.startswith("/"):
            _show(task_command("/plan " + text))
            continue
        result = run_command(text, on_chunk=live_printer())
        if result["kind"] == "exit":
            _print(result)
            break
        _print(result)



def _read():
    try:
        return read_input(service)
    except (EOFError, KeyboardInterrupt):
        return "/quit"


def _show(text):
    if text:
        print(decorate(text))


def _print(result):
    output = render(result)
    if output:
        print(output)
