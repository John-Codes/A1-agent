"""Real local HTTP helpers, deliberately fixed to the isolated review stack."""
import json
import requests

A1 = 'http://127.0.0.1:8137'
API = 'http://127.0.0.1:8136'
BASE = API + '/api/v1/workspaces/article_local/articles'
TOKEN = 'local-article-test-token'


def require_local_stack():
    health = requests.get(API + '/health', timeout=5).json()
    assert health['status'] == 'ok' and health['db'] == 'cdl_article_agent_local', health
    assert requests.get(A1 + '/health', timeout=5).json()['ok']


def tool(action, **params):
    response = requests.post(A1 + '/tool', json={
        'name': 'cdl_articles', 'body': json.dumps({'action': action, **params})}, timeout=35)
    response.raise_for_status()
    result = response.json()
    assert not result.get('error'), result
    return json.loads(result['response'])


def article(slug, lang='en'):
    return {'slug': slug, 'lang': lang, 'title': 'Local CDL article review',
            'description': 'Local integration test article for CDLTestReady.',
            'excerpt': 'Local-only integration test, not production content.',
            'publishedDate': '2026-10-15', 'tags': ['local-test'],
            'content': '## Study plan\n\nLocal article agent integration check. '
                       'Consult official materials for exam preparation.\n\n'
                       '[Practice tests](/practice-tests/)'}


def console(action, **params):
    text = '/cdl_articles ' + json.dumps({'action': action, **params})
    response = requests.post(A1 + '/command', json={'text': text}, timeout=35)
    response.raise_for_status()
    result = response.json()
    assert not result.get('error'), result
    return json.loads(result['response'])
