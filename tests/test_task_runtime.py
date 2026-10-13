import json
import os
import signal
import subprocess
import sys
import threading
import time

import pytest

from task_runtime import controller, state
from task_runtime.policy import enforce
from task_runtime.read_file import read_project_file
from task_runtime.supervisor import EmergencyStop, supervise


def task(identifier='1', deps=None):
    return {'id': identifier, 'title': 'Inspect', 'instructions': 'Read',
            'check': 'Observed result', 'depends_on': deps or []}


def test_plan_validation_and_dependencies():
    tasks = state.validate_plan({'tasks': [task(), task('2', ['1'])]})
    data = {'tasks': tasks}
    assert state.next_task(data)['id'] == '1'
    tasks[0]['status'] = 'blocked'
    assert state.next_task(data) is None
    tasks[0]['status'] = 'done'
    assert state.next_task(data)['id'] == '2'
    with pytest.raises(ValueError):
        state.validate_plan({'tasks': [task('1', ['2'])]})


def test_durable_recovery(tmp_path):
    path = tmp_path / 'tasks.json'
    tasks = state.validate_plan({'tasks': [task()]})
    tasks[0]['status'] = 'running'
    state.save({'mode': 'execute', 'tasks': tasks}, path)
    assert state.load(path)['tasks'][0]['status'] == 'interrupted'
    assert path.stat().st_mode & 0o777 == 0o600


def test_plan_policy_blocks_side_effects(monkeypatch):
    from store import store
    monkeypatch.setitem(store, 'mode', 'plan')
    for name in ('shell', 'browser_use', 'memory_write', 'agentmail', 'trello_clone'):
        with pytest.raises(PermissionError):
            enforce(name)
    enforce('project_read')
    assert 'AOne' in read_project_file('README.md')
    for path in ('.env', '../.bashrc'):
        with pytest.raises((PermissionError, ValueError)):
            read_project_file(path)


def stalled_worker(connection, mode, payload):
    os.setsid()
    connection.send(('ready', os.getpid()))
    # A detached child simulates a browser escaping its parent's process group.
    child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'],
                             start_new_session=True)
    connection.send(('event', str(child.pid)))
    time.sleep(60)


def test_esc_kills_worker_and_detached_child():
    reader, writer = os.pipe()
    children = []

    def emit(message, **kwargs):
        children.append(int(message.split('|')[1]))
        os.write(writer, b'\x1b')

    try:
        started = time.monotonic()
        with pytest.raises(EmergencyStop):
            supervise('execute', {}, reader, emit=emit, target=stalled_worker)
        assert time.monotonic() - started < 5
        assert children
        for _ in range(40):
            path = f'/proc/{children[0]}/stat'
            try:
                with open(path) as stream:
                    stopped = stream.read().rsplit(')', 1)[1].split()[0] == 'Z'
            except (FileNotFoundError, ProcessLookupError):
                stopped = True
            if stopped:
                break
            time.sleep(.025)
        else:
            pytest.fail('Detached child survived emergency stop')
    finally:
        os.close(reader)
        os.close(writer)
