#!/usr/bin/env python3
"""drafts/portfolio/ の下書き（Markdown）を、公開済み記事の本文に反映する。

使い方:
  python3 scripts/sync_draft.py drafts/portfolio/16_xxx.md            # 本文だけ反映
  python3 scripts/sync_draft.py drafts/portfolio/16_xxx.md --updated  # 更新日も今日にする

下書きの先頭にフロントマター `slug:` を書くと、articles/<slug>/ の
index.html の <article> 内と index.md の本文を書き換える。
タイトル・説明文・関連記事など本文以外は書き換えない（H1が違う場合は警告だけ出す）。

下書きの書き方:
  ## 見出し / **太字** / [リンク](URL) / 表 / > 引用 / - 箇条書き
  ![代替テキスト](/assets/images/articles/xxx.webp "キャプション")  → 画像
  画像の行を空行なしで2つ続ける     → 2枚並べて表示（スマホでは縦に並ぶ）
  *【画像：…】*                     → まだ画像がない目印。公開ページには出さない
  表の直後の *…* だけの行           → 表の注記
  <!-- more --> の次の段落          → 枠付きの「関連記事」段落
"""
import datetime
import html
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG = re.compile(r'!\[([^\]]*)\]\((\S+)(?: "([^"]*)")?\)')
SITE = "https://miyazakimari.com"


def parse_front_matter(text):
    meta = {}
    if text.startswith("---\n"):
        end = text.index("\n---\n", 4)
        for line in text[4:end].splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
        text = text[end + 5:]
    return meta, text


def html_href(url):
    """サイト内URLは相対・ルート相対に、外部URLはそのまま。"""
    m = re.match(re.escape(SITE) + r"/articles/([^/]+)/$", url)
    if m:
        return f"../{m.group(1)}/", False
    if url.startswith(SITE + "/"):
        return url[len(SITE):], False
    return url, url.startswith("http")


def inline(text):
    text = html.escape(text, quote=False)

    def link(m):
        label, url = m.group(1), html.unescape(m.group(2))
        href, external = html_href(url)
        href = html.escape(href)
        if external:
            return (f'<a href="{href}" target="_blank" rel="noopener">{label}'
                    '<span class="sr-only">（新しいタブで開きます）</span></a>')
        return f'<a href="{href}">{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text


def is_placeholder(block):
    return re.fullmatch(r"\*【画像[：:].*】\*", block.strip()) is not None


def to_html(body):
    blocks = [b.strip("\n") for b in re.split(r"\n\s*\n", body.strip()) if b.strip()]
    out, more, prev_table = [], False, False
    for b in blocks:
        lines = b.splitlines()
        if b.strip() == "<!-- more -->":
            more = True
            continue
        if is_placeholder(b):
            continue
        if b.startswith("## "):
            out.append(f"<h2>{inline(b[3:].strip())}</h2>")
        elif all(l.startswith("|") for l in lines) and len(lines) >= 2:
            rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in lines]
            head, body_rows = rows[0], rows[2:]
            t = ['<div class="article-table">', "  <table>", "    <thead>",
                 "      <tr>" + "".join(f'<th scope="col">{inline(c)}</th>' for c in head) + "</tr>",
                 "    </thead>", "    <tbody>"]
            for r in body_rows:
                t.append("      <tr>" + f'<th scope="row">{inline(r[0])}</th>'
                         + "".join(f"<td>{inline(c)}</td>" for c in r[1:]) + "</tr>")
            t += ["    </tbody>", "  </table>", "</div>"]
            out.append("\n".join(t))
            prev_table = True
            continue
        elif prev_table and re.fullmatch(r"\*[^*].*\*", b.strip()):
            out.append(f'<p class="article-note">{inline(b.strip()[1:-1])}</p>')
        elif all(l.startswith(">") for l in lines):
            inner = "\n".join(re.sub(r"^> ?", "", l) for l in lines)
            paras = [p for p in re.split(r"\n\s*\n", inner) if p.strip()]
            out.append("<blockquote>\n" + "\n".join(
                f"  <p>{inline(' '.join(p.split()))}</p>" for p in paras) + "\n</blockquote>")
        elif all(re.match(r"[-*] ", l) for l in lines):
            out.append("<ul>\n" + "\n".join(f"  <li>{inline(l[2:].strip())}</li>" for l in lines) + "\n</ul>")
        elif all(IMG.fullmatch(l.strip()) for l in lines):
            imgs = [IMG.fullmatch(l.strip()).groups() for l in lines]

            def one(alt, src, cap, tag):
                f = [f'<{tag} class="article-figure">',
                     f'  <img src="{html.escape(html_href(src)[0])}" alt="{html.escape(alt)}" loading="lazy">']
                if cap:
                    f.append(f"  <figcaption>{inline(cap)}</figcaption>")
                f.append(f"</{tag}>")
                return f

            if len(imgs) == 1:
                out.append("\n".join(one(*imgs[0], "figure")))
            else:
                inner = [l for g in imgs for l in one(*g, "figure")]
                out.append('<div class="article-figure-pair">\n' + "\n".join("  " + l for l in inner) + "\n</div>")
        else:
            cls = ' class="article-more"' if more else ""
            out.append(f"<p{cls}>{inline(''.join(l.strip() for l in lines))}</p>")
        more = prev_table = False
    return "\n\n".join("\n".join("      " + l for l in o.splitlines()) for o in out) + "\n"


def to_md(body):
    """Markdown版用：画像の目印と more 記号を除く。"""
    blocks = [b for b in re.split(r"\n\s*\n", body.strip()) if b.strip()]
    keep = [b for b in blocks if b.strip() != "<!-- more -->" and not is_placeholder(b)]
    return "\n\n".join(keep) + "\n"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        sys.exit(__doc__)
    touch = "--updated" in sys.argv
    meta, text = parse_front_matter(Path(args[0]).read_text())
    slug = meta.get("slug") or sys.exit("下書きの先頭に slug: がありません")
    art = ROOT / "articles" / slug
    m = re.match(r"\s*# (.+)\n", text)
    title, body = (m.group(1).strip(), text[m.end():]) if m else (None, text)

    page = (art / "index.html").read_text()
    if title:
        h1 = re.sub(r"<[^>]+>", "", re.search(r"<h1>(.*?)</h1>", page, re.S).group(1))
        if h1 != title:
            print(f"注意: 下書きのタイトルが公開中のH1と違います（タイトル類は変更していません）\n  下書き: {title}\n  公開中: {h1}")

    new_body = to_html(body)
    page = re.sub(r"(<article>\n).*?(    </article>)", lambda x: x.group(1) + new_body + x.group(2), page, flags=re.S)
    plain = re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", new_body))
    page = re.sub(r'"wordCount": \d+', f'"wordCount": {len(html.unescape(plain))}', page)

    md_path = art / "index.md"
    md = md_path.read_text()
    head_end = md.index("\n\n", md.index("\n# ") + 1)          # H1
    head_end = md.index("\n\n", head_end + 2)                   # 著者・日付の行
    tail_i = md.find("\n---\n\n## この続きを読む")
    md = md[:head_end + 2] + to_md(body) + (md[tail_i:] if tail_i != -1 else "")

    if touch:
        today = datetime.date.today().isoformat()
        jp = f"{datetime.date.today().year}年{datetime.date.today().month}月{datetime.date.today().day}日"
        page = re.sub(r'(article:modified_time" content=")[^"]*', rf"\g<1>{today}", page)
        page = re.sub(r'("dateModified": ")[^"]*', rf"\g<1>{today}", page)
        if "<span>更新 <time" in page:
            page = re.sub(r'<span>更新 <time datetime="[^"]*">[^<]*</time></span>',
                          f'<span>更新 <time datetime="{today}">{jp}</time></span>', page)
        else:
            page = re.sub(r'(      <span>公開 <time[^\n]*</span>\n)',
                          rf'\g<1>      <span>更新 <time datetime="{today}">{jp}</time></span>\n', page, count=1)
        md = re.sub(r"(?m)^updated: .*$", f"updated: {today}", md)
        md = re.sub(r"(／公開 \d{4}-\d{2}-\d{2})(・更新 \d{4}-\d{2}-\d{2})?", rf"\g<1>・更新 {today}", md, count=1)
        if f"公開 {today}・更新 {today}" in md:
            md = md.replace(f"・更新 {today}", "", 1)
        sm = ROOT / "sitemap.xml"
        sm.write_text(re.sub(r"(<loc>" + re.escape(f"{SITE}/articles/{slug}/") + r"</loc>\s*<lastmod>)[^<]*",
                             rf"\g<1>{today}", sm.read_text()))

    (art / "index.html").write_text(page)
    md_path.write_text(md)
    print(f"反映しました: articles/{slug}/index.html, index.md" + ("（更新日も変更）" if touch else ""))
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_llms_full.py")], check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "check_site.py")], check=True)


if __name__ == "__main__":
    main()
