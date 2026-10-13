import os
import sys
import termios

import pytest

from task_runtime.supervisor import supervise
from task_runtime.terminal import keyboard
from tests.test_task_runtime import stalled_worker


def test_timeout_terminates_stalled_worker():
    reader, writer = os.pipe()
    try:
        with pytest.raises(TimeoutError):
            supervise('execute', {}, reader, emit=lambda *a, **k: None,
                      timeout=.15, target=stalled_worker)
    finally:
        os.close(reader)
        os.close(writer)


def test_keyboard_restores_terminal_after_error(monkeypatch):
    master, slave = os.openpty()
    stream = os.fdopen(os.dup(slave))
    monkeypatch.setattr(sys, 'stdin', stream)
    original = termios.tcgetattr(slave)
    try:
        with pytest.raises(RuntimeError):
            with keyboard():
                assert not termios.tcgetattr(slave)[3] & termios.ICANON
                raise RuntimeError('stop')
        assert termios.tcgetattr(slave) == original
    finally:
        stream.close()
        os.close(master)
        os.close(slave)


def test_dispatcher_enforces_policy_before_handler(monkeypatch):
    from store import store
    from tools import dispatcher
    monkeypatch.setitem(store, 'mode', 'plan')
    monkeypatch.setitem(dispatcher.TOOL_HANDLERS, 'agentmail',
                        lambda body: pytest.fail('Side effect reached'))
    with pytest.raises(PermissionError):
        dispatcher.dispatch_tool_call({'name': 'agentmail', 'body': 'send'})
