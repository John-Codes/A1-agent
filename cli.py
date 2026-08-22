import time

import agent
from commands import run as run_command
from config import TICK_INTERVAL_SECONDS
from features.terminal_output import input_prompt, render


def main():
    last_tick = time.monotonic()
    print("Personal AI Gateway")
    print("Type a message, /life_log <entry>, /history, /tools, /search <query>, /tick, /memory, /log, or /quit.")

    while True:
        result = run_command(_read())
        if result["kind"] == "exit":
            _print(result)
            break
        _print(result)

        if time.monotonic() - last_tick >= TICK_INTERVAL_SECONDS:
            _print({"kind": "tick", **agent.tick()})
            last_tick = time.monotonic()


def _read():
    try:
        return input(input_prompt())
    except EOFError:
        return "/quit"


def _print(result):
    output = render(result)
    if output:
        print(output)
