#!/usr/bin/env python3
"""見出し・タイトルの文節の切れ目に <wbr> を入れる（Safari 対策）。

Chrome は CSS の word-break: auto-phrase で文節改行できるが、Safari は未対応で、
「モデ／ル」のように単語の途中で折り返す。そこで BudouX（pip install budoux）で
文節を判定し、対象要素の中に <wbr> を入れる。Safari 側は site.css の
@supports で word-break: keep-all にして、<wbr> の位置でだけ折り返させる。

使い方:
  python3 scripts/add_wbr.py            # サイト内の全HTMLを処理
  python3 scripts/add_wbr.py a.html ... # 指定したファイルだけ

何度実行しても同じ結果になる（既存の <wbr> を外してから入れ直す）。
対象は TARGET_TAGS と TARGET_CLASSES。site.css の auto-phrase の対象を増やしたら、ここにも足す。
"""
import re
import sys
from pathlib import Path

import budoux

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"drafts", "design", "screenshots", "archive", "node_modules", ".git", ".claude"}
TARGET_TAGS = ["h1", "h2", "h3", "h4"]
TARGET_CLASSES = [
    "article-title", "articles-title", "start-q", "related-title", "related-question",
    "read-next-title", "news-title", "event-title", "cta-banner-title",
    "contact-success-title", "media-archive-title", "award-highlight-name",
    "award-highlight-subtitle", "book-catch", "book-subtitle", "hero-tagline",
    "hero-expertise", "lead", "hero-intro", "web-media-lead",
]

KEEP_TOGETHER = ["わが家"]

parser = budoux.load_default_japanese_parser()
TAG = re.compile(r"<[^>]+>")
JP = re.compile(r"[぀-ヿ㐀-鿿]")


def add_wbr(inner):
    inner = inner.replace("<wbr>", "")
    parts = TAG.split(inner)
    tags = TAG.findall(inner)
    text = "".join(parts)
    if not JP.search(text):
        return inner
    # 文節の境目（テキスト全体での文字位置）
    cuts, pos = set(), 0
    for chunk in parser.parse(text)[:-1]:
        pos += len(chunk)
        cuts.add(pos)
    # BudouX が分けてしまうが、途中で切りたくない語
    for word in KEEP_TOGETHER:
        for m in re.finditer(re.escape(word), text):
            cuts -= set(range(m.start() + 1, m.end()))
    out, offset = [], 0
    for i, part in enumerate(parts):
        buf = []
        for j, ch in enumerate(part):
            k = offset + j
            if k in cuts and j > 0 and not part[j - 1].isspace() and not ch.isspace():
                buf.append("<wbr>")
            buf.append(ch)
        out.append("".join(buf))
        offset += len(part)
        if i < len(tags):
            out.append(tags[i])
    return "".join(out)


def find_close(html, tag, start):
    """start（開始タグの直後）から、同名タグの入れ子を数えて対応する閉じタグの位置を返す。"""
    depth, i = 1, start
    pat = re.compile(rf"<(/?){tag}\b[^>]*>", re.I)
    while True:
        m = pat.search(html, i)
        if not m:
            return None
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return m.start()
        i = m.end()


def process(html):
    body_at = html.find("<body")
    if body_at == -1:
        return html
    head, body = html[:body_at], html[body_at:]
    cls_alt = "|".join(map(re.escape, TARGET_CLASSES))
    opener = re.compile(
        rf'<(?P<t>{"|".join(TARGET_TAGS)})\b[^>]*>|<(?P<c>[a-z0-9]+)\b[^>]*\bclass="(?:[^"]*\s)?(?:{cls_alt})(?:\s[^"]*)?"[^>]*>',
        re.I)
    out, i = [], 0
    while True:
        m = opener.search(body, i)
        if not m:
            out.append(body[i:])
            break
        tag = (m.group("t") or m.group("c")).lower()
        close = find_close(body, tag, m.end())
        if close is None:
            out.append(body[i:m.end()])
            i = m.end()
            continue
        out.append(body[i:m.end()])
        out.append(add_wbr(body[m.end():close]))
        i = close
    return head + "".join(out)


def targets(args):
    if args:
        return [Path(a) for a in args]
    return [p for p in ROOT.rglob("*.html")
            if not (set(p.relative_to(ROOT).parts) & SKIP_DIRS)]


def main():
    changed = 0
    for p in targets(sys.argv[1:]):
        src = p.read_text()
        new = process(src)
        if new != src:
            p.write_text(new)
            changed += 1
    print(f"<wbr>: {changed} files updated")


if __name__ == "__main__":
    main()
