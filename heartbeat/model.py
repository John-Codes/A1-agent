from heartbeat import settings


def complete(prompt, shared):
    if settings.PROVIDER != 'ollama':
        from llm_client import complete_prompt
        return complete_prompt(prompt, shared)
    try:
        return _ollama_complete(prompt)
    except Exception as exc:
        from tools.log import log_exception, report_model_failure
        log_exception('heartbeat.model', exc)
        report_model_failure(settings.PROVIDER, settings.MODEL, exc)
        raise


def _ollama_complete(prompt):
    import requests
    response = requests.post(
        settings.API_BASE.rstrip('/') + '/api/chat',
        json={'model': settings.MODEL, 'messages': [{'role': 'user', 'content': prompt}],
              'stream': False, 'think': False,
              'options': {'num_ctx': 4096, 'num_predict': 128}},
        timeout=settings.TIMEOUT,
    )
    response.raise_for_status()
    text = response.json().get('message', {}).get('content', '').strip()
    if not text:
        raise ValueError('Heartbeat model returned no text.')
    return {'ok': True, 'text': text}
