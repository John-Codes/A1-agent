import llm_client


def large_response(prompt, route, image_data, queue):
    queue.put({'ok': True, 'text': 'article ' * 100000})


def test_large_response_is_drained_before_join(monkeypatch):
    monkeypatch.setattr(llm_client, '_route_worker', large_response)
    monkeypatch.setattr(llm_client, 'LLM_GENERATION_TIMEOUT', 5)
    result = llm_client._try_route('write', {'provider': 'test', 'model': 'test'})
    assert result['ok']
    assert len(result['text']) == 800000
