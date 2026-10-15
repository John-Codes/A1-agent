"""Thin HTTP tool; the article API owns its instructions and workflow."""
import json
import os
from urllib.parse import quote, urlparse

import requests


def run(body):
    data = json.loads(body or '{}')
    if not isinstance(data, dict):
        raise ValueError('Expected a JSON object; use {} for API instructions.')
    base = os.environ.get('CDL_ARTICLE_API_URL', '').rstrip('/')
    parsed = urlparse(base)
    if parsed.scheme not in {'http', 'https'} or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError('Set CDL_ARTICLE_API_URL to the exam API base URL.')
    workspace = os.environ.get('CDL_ARTICLE_WORKSPACE', 'ws_1')
    url = f'{base}/api/v1/workspaces/{quote(workspace, safe="")}/articles'
    action = data.get('action', 'instructions')
    headers = {'Accept': 'application/json'}
    token = os.environ.get('CDL_ARTICLE_ADMIN_TOKEN', '')
    if action not in {'instructions', 'get', 'list'} and not token:
        raise ValueError('Set CDL_ARTICLE_ADMIN_TOKEN for article writes.')
    if token:
        headers['X-Admin-Token'] = token
    if action == 'instructions':
        response = requests.get(url + '/agent/instructions', headers=headers, timeout=30, allow_redirects=False)
    else:
        response = requests.post(url + '/agent', json=data, headers=headers, timeout=30, allow_redirects=False)
    if not 200 <= response.status_code < 300:
        raise RuntimeError(f'CDLTestReady API HTTP {response.status_code}: {response.text[:1200]}')
    return json.dumps(response.json(), ensure_ascii=False)
