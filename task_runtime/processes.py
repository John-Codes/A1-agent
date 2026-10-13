import os
import signal
from pathlib import Path


def descendants(pid):
    parents = {}
    for entry in Path("/proc").glob("[0-9]*/stat"):
        try:
            fields = entry.read_text().rsplit(")", 1)[1].split()
            parents[int(entry.parent.name)] = int(fields[1])
        except (OSError, ValueError, IndexError):
            continue
    found = {pid}
    while True:
        expanded = found | {child for child, parent in parents.items() if parent in found}
        if expanded == found:
            return found - {pid}
        found = expanded


def kill(pid, grouped):
    # Freeze the worker before collecting children so it cannot launch more work.
    _signal(pid, signal.SIGSTOP)
    children = descendants(pid)
    for child in children:
        _signal(child, signal.SIGSTOP)
    children |= descendants(pid)
    if grouped:
        try:
            os.killpg(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    for child in children:
        _signal(child, signal.SIGKILL)
    _signal(pid, signal.SIGKILL)


def _signal(pid, sig):
    try:
        os.kill(pid, sig)
    except ProcessLookupError:
        pass
