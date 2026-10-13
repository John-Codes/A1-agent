import pytest

from task_runtime import controller, state
from task_runtime.supervisor import EmergencyStop


def setup(monkeypatch):
    tasks = state.validate_plan({'tasks': [
        {'id': '1', 'title': 'One', 'instructions': 'Do', 'check': 'Verify'},
        {'id': '2', 'title': 'Two', 'instructions': 'Do', 'check': 'Verify',
         'depends_on': ['1']}]})
    saved = []
    monkeypatch.setattr(controller, 'save', lambda data: saved.append(str(data)))
    return {'mode': 'plan', 'goal': 'Test', 'tasks': tasks}, saved


def test_drains_queue(monkeypatch):
    data, saved = setup(monkeypatch)
    calls = []
    def work(mode, payload, fd, **kwargs):
        calls.append(payload['task']['id'])
        return {'status': 'done', 'evidence': 'Read back expected result'}
    monkeypatch.setattr(controller, 'supervise', work)
    controller.execute(data, 0)
    assert calls == ['1', '2']
    assert all(t['status'] == 'done' for t in data['tasks'])


def test_invalid_completion_blocks_dependents(monkeypatch):
    data, saved = setup(monkeypatch)
    monkeypatch.setattr(controller, 'supervise', lambda *a, **k: {'status': 'done'})
    controller.execute(data, 0)
    assert [t['status'] for t in data['tasks']] == ['failed', 'pending']


def test_stop_persists_and_never_continues(monkeypatch):
    data, saved = setup(monkeypatch)
    def stop(*args, **kwargs):
        raise EmergencyStop()
    monkeypatch.setattr(controller, 'supervise', stop)
    with pytest.raises(EmergencyStop):
        controller.execute(data, 0)
    assert data['mode'] == 'stopped'
    assert [t['status'] for t in data['tasks']] == ['interrupted', 'pending']
    assert 'interrupted' in saved[-1]


def test_resume_attempt_limit(monkeypatch):
    data, saved = setup(monkeypatch)
    data['tasks'][0].update(status='failed', attempts=3)
    monkeypatch.setattr(controller, 'supervise', lambda *a, **k: pytest.fail('Unexpected work'))
    controller.execute(data, 0, resume=True)
    assert data['tasks'][0]['status'] == 'failed'
