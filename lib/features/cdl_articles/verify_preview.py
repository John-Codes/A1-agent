"""Assert published API content reaches built pages served over local HTTP."""
import requests
from .local_http import BASE, require_local_stack


def main():
    require_local_stack()
    for lang, prefix in [('en', ''), ('es', '/es')]:
        slug = 'local-article-agent-review-' + lang
        article = requests.get(BASE + '/' + slug, timeout=5).json()
        page = requests.get(f'http://127.0.0.1:8138{prefix}/blog/{slug}/', timeout=5)
        page.encoding = 'utf-8'  # Astro declares UTF-8; Python's static server omits the charset.
        assert page.status_code == 200
        assert article['title'] in page.text
        assert 'Sergio' in page.text
        assert article['status'] == 'published'
        marker = 'Local article agent integration check' if lang == 'en' else 'Este artículo verifica'
        assert marker in page.text
        index = requests.get(f'http://127.0.0.1:8138{prefix}/blog/', timeout=5)
        index.encoding = 'utf-8'
        assert f'href="{prefix}/blog/{slug}/"' in index.text
    print('PASS: real A1 → API → MongoDB → site sync → Astro build → HTTP EN/ES pages and index links.')


if __name__ == '__main__':
    main()
