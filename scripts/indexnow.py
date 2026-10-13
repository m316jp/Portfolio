#!/usr/bin/env python3
"""IndexNow（Bingなど）に更新したURLを通知する。標準ライブラリのみ。

使い方:
  python3 scripts/indexnow.py                 # sitemap.xml の全URLを通知
  python3 scripts/indexnow.py --since 2026-10-13  # lastmod がこの日以降のURLだけ
  python3 scripts/indexnow.py https://miyazakimari.com/articles/xxx/  # 指定URLだけ

公開（git push）してサイトに反映されてから実行する。
"""
from pathlib import Path
import json
import re
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
HOST = 'miyazakimari.com'
KEY = 'd7f030e362a06eb79f8170c52aa44321'
ENDPOINT = 'https://api.indexnow.org/indexnow'


def sitemap_urls(since=None):
    text = (ROOT / 'sitemap.xml').read_text()
    urls = []
    for block in re.findall(r'<url>(.*?)</url>', text, re.S):
        loc = re.search(r'<loc>(.*?)</loc>', block).group(1).strip()
        lastmod = re.search(r'<lastmod>(.*?)</lastmod>', block)
        if since and (not lastmod or lastmod.group(1).strip()[:10] < since):
            continue
        urls.append(loc)
    return urls


def main(args):
    if args[:1] == ['--since']:
        urls = sitemap_urls(args[1])
    elif args:
        urls = args
    else:
        urls = sitemap_urls()
    if not urls:
        print('通知するURLがありません。')
        return 0
    if not (ROOT / f'{KEY}.txt').exists():
        print(f'キーファイル {KEY}.txt がリポジトリにありません。')
        return 1
    body = json.dumps({
        'host': HOST,
        'key': KEY,
        'keyLocation': f'https://{HOST}/{KEY}.txt',
        'urlList': urls,
    }).encode()
    req = urllib.request.Request(ENDPOINT, data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            status = res.status
    except urllib.error.HTTPError as e:
        status = e.code
    for u in urls:
        print('  ' + u)
    # 200: 受理 / 202: 受理（キー確認待ち） / 403: キー不一致 / 422: URLとホスト不一致 / 429: 送りすぎ
    print(f'IndexNow: {len(urls)}件を送信 → HTTP {status}')
    return 0 if status in (200, 202) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
