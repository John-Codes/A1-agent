from commands import run as run_command
from task_runtime.controller import command as task_command
from task_runtime.state import PATH
from store import store
from features.terminal_output import render
from heartbeat.service import service
from heartbeat.console import read_input


def main():
    service.start()
    try:
        _loop()
    finally:
        service.close()


def _loop():
    print("Personal AI Gateway")
    print("Type a message, /life_log <entry>, /history, /tools, /search <query>, /tick, /memory, /log, or /quit.")

    print("Tasks: /plan <goal>, /execute, /status, /resume. Esc stops active task work.")
    if PATH.exists():
        store["mode"] = "plan"
    while True:
        text = _read()
        if text.strip() == '/tick':
            print(service.request())
            continue
        if text.split(maxsplit=1)[:1] == ['/heartbeat']:
            action = text.partition(' ')[2].strip()
            if action == 'resume':
                print(service.resume())
            elif action == 'stop':
                service.stop()
                print('Heartbeat paused.')
            else:
                print(service.status())
            continue
        task_result = task_command(text.strip())
        if task_result is not None:
            store["mode"] = "plan"
            print(task_result)
            if text.strip() == '/status':
                print(service.status())
            continue
        if store.get("mode") == "plan" and text.strip() and not text.startswith("/"):
            print(task_command("/plan " + text))
            continue
        result = run_command(text)
        if result["kind"] == "exit":
            _print(result)
            break
        _print(result)



def _read():
    try:
        return read_input(service)
    except (EOFError, KeyboardInterrupt):
        return "/quit"


def _print(result):
    output = render(result)
    if output:
        print(output)
