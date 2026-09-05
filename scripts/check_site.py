#!/usr/bin/env python3
"""標準ライブラリのみでサイト内リンク・画像・構造化データを確認する。"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import re

ROOT = Path(__file__).resolve().parent.parent
SKIP = {'.git', '.claude', '.vscode', 'archive', 'drafts', 'node_modules'}

class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.ids = set()
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for name in ('src', 'href', 'poster'):
            if attrs.get(name):
                self.links.append(attrs[name])
        if tag == 'meta' and attrs.get('property', attrs.get('name', '')) in {'og:image', 'twitter:image'}:
            self.links.append(attrs.get('content', ''))

pages = {p: Document(p.read_text()) for p in ROOT.rglob('*.html') if not SKIP.intersection(p.relative_to(ROOT).parts)}
errors = []
checks = 0

def check_url(page, url):
    global checks
    u = urlsplit(url)
    if u.scheme and u.scheme not in {'http', 'https'}:
        return
    if u.netloc and u.netloc != 'miyazakimari.com':
        return
    target = (ROOT / unquote(u.path).lstrip('/')) if u.netloc or u.path.startswith('/') else (page.parent / unquote(u.path) if u.path else page)
    target = target.resolve()
    if target.is_dir():
        target /= 'index.html'
    checks += 1
    if not target.exists():
        errors.append(f'{page.relative_to(ROOT)}: missing {url}')
    elif u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids:
        errors.append(f'{page.relative_to(ROOT)}: missing anchor {url}')

def structured_urls(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from structured_urls(item)
    elif isinstance(value, list):
        for item in value:
            yield from structured_urls(item)
    elif isinstance(value, str) and value.startswith('https://miyazakimari.com/'):
        # JSON-LD @id fragments name schema entities, not HTML anchors.
        yield value.split('#')[0]

for page, doc in pages.items():
    text = page.read_text()
    for url in doc.links + re.findall(r'url\([\s\'\"]*([^\)\'\"\s]+)', text):
        check_url(page, url)
    for block in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', text, re.S):
        try:
            for url in structured_urls(json.loads(block)):
                check_url(page, url)
        except json.JSONDecodeError as e:
            errors.append(f'{page.relative_to(ROOT)}: invalid JSON-LD {e}')

for url in re.findall(r'<loc>(.*?)</loc>', (ROOT / 'sitemap.xml').read_text()):
    check_url(ROOT / 'index.html', url)
if errors:
    print('\n'.join(errors))
    raise SystemExit(1)
print(f'OK: {len(pages)} HTML files, {checks} local references; JSON-LD and sitemap checked.')
