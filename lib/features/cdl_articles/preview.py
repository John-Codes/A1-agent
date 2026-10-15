"""Publish two local-only review articles via the real A1 HTTP tool."""
from .local_http import BASE, TOKEN, article, require_local_stack, tool
import requests


def main():
    require_local_stack()
    for lang in ('en', 'es'):
        slug = 'local-article-agent-review-' + lang
        payload = article(slug, lang)
        payload['author'] = 'Sergio'
        if lang == 'es':
            payload.update(title='Revisión local de publicación CDL',
                           content='## Prueba local\n\nEste artículo verifica la integración local de A1 con CDLTestReady. '
                                   'No es contenido para producción.\n\n[Práctica CDL](/practice-tests/)')
        existing = requests.get(BASE + '/' + slug, headers={'X-Admin-Token': TOKEN}, timeout=5)
        if existing.status_code == 404:
            tool('create', article=payload)
        else:
            existing.raise_for_status()
            tool('update', slug=slug, article=payload)
        assert tool('publish', slug=slug)['article']['status'] == 'published'
        assert requests.get(BASE + '/' + slug, timeout=5).json()['content'] == payload['content']
    print('Local EN/ES review articles published to isolated API through A1.')


if __name__ == '__main__':
    main()
