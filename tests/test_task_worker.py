import pytest

from task_runtime.worker import generate, parse_json


class Events:
    def __init__(self):
        self.items = []

    def send(self, event):
        self.items.append(event)


def test_worker_stops_repeated_tool_results(monkeypatch):
    import context
    import llm_client
    import tools
    monkeypatch.setattr(context, 'load_context_prompt', lambda query: '')
    monkeypatch.setattr(llm_client, 'complete_prompt', lambda *args: {
        'ok': True, 'text': '<tool name="memory_search">same</tool>'})
    monkeypatch.setattr(tools, 'dispatch_tool_call', lambda call: 'unchanged')
    events = Events()
    with pytest.raises(RuntimeError, match='No progress'):
        generate('plan', {'goal': 'Investigate'}, events)
    assert len(events.items) == 3


def test_structured_result_parsing():
    assert parse_json('```json\n{"status":"blocked"}\n```')['status'] == 'blocked'
    with pytest.raises(ValueError):
        parse_json('[]')
