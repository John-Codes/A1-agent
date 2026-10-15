"""Run: python -m lib.features.cdl_articles.e2e (real HTTP + Docker MongoDB)."""
import json
import uuid
import requests
from .local_http import BASE, TOKEN, article, console, require_local_stack, tool


def main():
    require_local_stack()
    contract = tool('instructions')
    assert 'publish' in contract['actions']
    assert contract['destination'] == 'https://cdltestready.com'
    prefix = 'local-e2e-' + uuid.uuid4().hex[:8]
    slugs = [prefix + '-en', prefix + '-es']
    try:
        for slug, lang in zip(slugs, ('en', 'es')):
            payload = article(slug, lang)
            assert tool('validate', article=payload)['ok']
            create = console if lang == 'es' else tool
            saved = create('create', article={**payload, 'status': 'published'})['article']
            assert saved['status'] == 'draft' and saved['author'] == 'Sergio'
            assert saved['created_at'] and saved['updated_at']
            assert requests.get(BASE + '/' + slug, timeout=5).status_code == 404
            assert tool('get', slug=slug)['content'] == payload['content']
            assert tool('list', status='draft', limit=1, page=1)
            duplicate = requests.post(BASE + '/agent', headers={'X-Admin-Token': TOKEN},
                                      json={'action': 'create', 'article': payload}, timeout=5)
            assert duplicate.status_code == 409
            denied = requests.post(BASE + '/agent', json={'action': 'publish', 'slug': slug}, timeout=5)
            assert denied.status_code == 401
            changed = tool('update', slug=slug, article={'author': 'Sergio', 'title': 'Reviewed local article'})
            assert changed['article']['content'] == payload['content']
            published = tool('publish', slug=slug)
            assert published['deployment'] == 'pending_site_sync'
            assert published['article']['status'] == 'published'
            public = requests.get(BASE + '/' + slug, timeout=5).json()
            assert public['title'] == 'Reviewed local article' and public['lang'] == lang
            assert tool('publish', slug=slug)['article']['id'] == saved['id']
            assert tool('update', slug=slug, article={'title': 'Edited'})['article']['status'] == 'draft'
            assert requests.get(BASE + '/' + slug, timeout=5).status_code == 404
        for data in ({'publishedDate': 'yesterday'}, {'content': '---\ntitle: bad\n---'}, {'author': ''}):
            response = requests.post(BASE + '/agent', headers={'X-Admin-Token': TOKEN},
                json={'action': 'validate', 'article': {**article(prefix), **data}}, timeout=5)
            assert response.status_code == 422, response.text
        other = BASE.replace('article_local', 'other_local_workspace')
        assert requests.get(other + '/' + slugs[0], headers={'X-Admin-Token': TOKEN}, timeout=5).status_code == 404
    finally:
        for slug in slugs:
            response = requests.get(BASE + '/' + slug, headers={'X-Admin-Token': TOKEN}, timeout=5)
            if response.status_code == 200:
                assert tool('delete', slug=slug)['deleted'] == slug
                assert requests.get(BASE + '/' + slug, timeout=5).status_code == 404
    print(json.dumps({'passed': True, 'coverage': 'A1 HTTP tool → exam API → real local MongoDB; EN/ES CRUD, validation, auth, publish, replay, isolation, delete'}))


if __name__ == '__main__':
    main()
