#!/usr/bin/env python3
"""llms.txt と記事のMarkdown版から llms-full.txt を生成する。"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://miyazakimari.com'


def load_article(path):
    text = path.read_text()
    m = re.match(r'---\n(.*?)\n---\n', text, re.S)
    if not m:
        raise SystemExit(f'{path.relative_to(ROOT)}: frontmatter がありません')
    meta = dict(re.findall(r'^(\w+): "?(.*?)"?$', m.group(1), re.M))
    body = text[m.end():].strip()
    base = meta['url']
    # 相対リンクは単体で読まれると解決できないので絶対URLにする
    body = re.sub(r'\]\(\.\./([^)]*)\)', lambda x: f']({SITE}/articles/{x.group(1)})', body)
    body = re.sub(r'\]\((?!https?://|#)([^)]*)\)', lambda x: f']({base}{x.group(1)})', body)
    return meta, body


articles = [load_article(p) for p in (ROOT / 'articles').glob('*/index.md')]
articles.sort(key=lambda a: a[0]['date'], reverse=True)

parts = [(ROOT / 'llms.txt').read_text().rstrip(), '', '# 記事全文', '']
for meta, body in articles:
    parts += [
        '---',
        '',
        f"URL: {meta['url']}",
        f"公開: {meta['date']} / 更新: {meta.get('updated', meta['date'])}",
        '',
        body,
        '',
    ]

(ROOT / 'llms-full.txt').write_text('\n'.join(parts).rstrip() + '\n')
print(f'llms-full.txt: {len(articles)} articles')
