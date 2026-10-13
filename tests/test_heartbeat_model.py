from heartbeat import model, settings
from llm_runtime import active_routes, set_active


def test_main_fallbacks_exclude_reserved_model(monkeypatch):
    import llm_runtime
    main = {'provider': 'ollama', 'model': 'main', 'api_base': '', 'label': 'default'}
    reserved = {'provider': settings.PROVIDER, 'model': settings.MODEL,
                'api_base': '', 'label': 'fallback_1'}
    monkeypatch.setattr(llm_runtime, 'default_route', lambda: main)
    monkeypatch.setattr(llm_runtime, 'fallback_routes', lambda: [reserved])
    assert active_routes({}) == [main]
    shared = {}
    set_active(shared, settings.PROVIDER, settings.MODEL, override=True,
               strict=True, label='heartbeat')
    assert len(active_routes(shared)) == 1
    assert active_routes(shared)[0]['model'] == settings.MODEL


def test_local_heartbeat_has_small_independent_request(monkeypatch):
    import requests
    monkeypatch.setattr(settings, 'PROVIDER', 'ollama')
    seen = {}
    class Response:
        def raise_for_status(self):
            pass
        def json(self):
            return {'message': {'content': 'No pending work.'}}
    def post(url, **kwargs):
        seen.update(kwargs)
        return Response()
    monkeypatch.setattr(requests, 'post', post)
    assert model.complete('Review tasks', {})['ok']
    assert seen['json']['model'] == settings.MODEL
    assert seen['json']['think'] is False
    assert seen['json']['options'] == {'num_ctx': 4096, 'num_predict': 128}
    assert seen['timeout'] == settings.TIMEOUT
