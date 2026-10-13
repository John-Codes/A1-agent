import json
import threading

import pytest

from heartbeat import report, settings, worker
from heartbeat.service import Heartbeat


@pytest.fixture(autouse=True)
def local_report(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, 'PATH', tmp_path / 'heartbeat.json')


def test_worker_uses_only_heartbeat_route_and_preserves_queue(monkeypatch, tmp_path):
    import config
    import heartbeat.model
    import llm_runtime
    from store import store
    from task_runtime import state
    queue = tmp_path / 'tasks.json'
    queue.write_text(json.dumps({'tasks': [{'status': 'running', 'title': 'Working'}]}))
    monkeypatch.setattr(state, 'PATH', queue)
    monkeypatch.setattr(config, 'CONTEXT_DIR', tmp_path)
    monkeypatch.setattr(settings, 'MODEL', 'separate-small-model')
    before = dict(store)
    def complete(prompt, shared):
        routes = llm_runtime.active_routes(shared)
        assert len(routes) == 1
        assert routes[0]['model'] == 'separate-small-model'
        assert '"status": "running"' in prompt
        assert shared is not store
        return {'ok': True, 'text': 'One task is running.'}
    monkeypatch.setattr(heartbeat.model, 'complete', complete)
    assert worker.check({})['speaker_name'] == 'heartbeat'
    assert store == before
    assert json.loads(queue.read_text())['tasks'][0]['status'] == 'running'


def test_overlap_rejected_before_model_call(monkeypatch):
    import heartbeat.model
    import llm_runtime
    monkeypatch.setattr(llm_runtime, 'active_routes', lambda shared: [
        {'provider': settings.PROVIDER, 'model': settings.MODEL}])
    monkeypatch.setattr(heartbeat.model, 'complete', lambda *a: pytest.fail('Called main model'))
    with pytest.raises(ValueError, match='overlaps'):
        worker.check({})


def test_tick_does_not_acquire_main_lock(monkeypatch):
    import agent
    from heartbeat.service import service
    monkeypatch.setattr(service, 'tick', lambda: {'response': 'isolated'})
    with agent._lock:
        assert agent.tick()['response'] == 'isolated'


def test_scheduler_runs_without_terminal_input(monkeypatch):
    heartbeat = Heartbeat()
    called = threading.Event()
    monkeypatch.setattr(settings, 'INTERVAL', .01)
    monkeypatch.setattr(heartbeat, 'tick', lambda **kwargs: called.set())
    heartbeat.paused = False
    heartbeat.start()
    try:
        assert called.wait(1)
        heartbeat.stop()
        assert heartbeat.cancel.is_set()
        assert heartbeat.paused
        heartbeat.resume()
        assert not heartbeat.cancel.is_set()
    finally:
        heartbeat.close()
    assert not heartbeat.thread.is_alive()


def test_duplicate_and_paused_checks_do_not_start_workers(monkeypatch):
    import heartbeat.service as module
    heartbeat = Heartbeat()
    monkeypatch.setattr(module, 'supervise', lambda *a, **k: pytest.fail('Unexpected worker'))
    heartbeat.stop()
    assert 'paused' in heartbeat.tick()['response']
    heartbeat.resume()
    with heartbeat.busy:
        assert 'already running' in heartbeat.tick()['response']
    report.record('done', 'Nothing pending')
    assert 'not due' in heartbeat.tick(scheduled=True)['response']
    assert 'Nothing pending' in heartbeat.status()
