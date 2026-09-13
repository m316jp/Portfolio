# サイト更新の記録

- サイトを大きく更新するときは、変更前と変更後のスクリーンショットを保存する。
- スクリーンショットのタイトルとファイル名には必ず撮影日（YYYY-MM-DD）を入れる。
- `screenshots/YYYY-MM-DD/` に、PC・スマホの表示と変更箇所が後から比較できる形で残す。
- 同日の記録は上書きせず、必要に応じて時刻や変更内容を付ける。

# ファイル配置

- 公開画像は `assets/images/` 以下に用途別・内容のわかる名前で保存する。移動・改名時はHTML・CSS・JSON-LD・サムネイル原稿の参照も更新する。
- 未公開原稿は `drafts/`、元写真は `archive/source-images/`、生成画像は `design/exports/` に保管する。これらはGit対象外。
- 記事の公開URLは `articles/<slug>/`、書籍ページは `book/` を維持する。
- ファイルの移動後は `python3 scripts/check_site.py` で参照を確認する。
- 詳細は `README.md` と `docs/2026-09-05-file-organization.md` を参照。

# 新しい記事を公開するときのチェックリスト

新規記事は `articles/what-to-ask-generative-ai/index.html` を正のテンプレートとしてコピーして作る（フィールドを個別に手打ちしない）。過去に実際抜けていた項目ばかりなので、公開前に必ず全部確認する。

- [ ] `<title>` は本文見出し（H1）とは別に、他記事と同程度の長さ（15〜36文字程度）で作る。H1をそのままコピーすると長くなりすぎて検索結果で切れる。
- [ ] `<meta name="description">` は120〜160文字程度。**文字数を確認する時は `wc -m` ではなく `python3 -c "print(len(open('f').read()))"` を使う**（このリポジトリのシェル環境は `LANG=C` なので `wc -m` は日本語をバイト数で数えてしまい、実際の3倍近い数字が出て見誤る）。
- [ ] OGP一式（og:site_name / og:type=article / og:locale / og:title / og:description / og:url / og:image / og:image:width,height / article:published_time / article:modified_time / article:author）と、Twitterカード一式（twitter:card / title / description / image）。
- [ ] `<link rel="alternate" type="application/rss+xml" href="/articles/feed.xml" title="生成AIと暮らしの話">` をheadに入れる。
- [ ] JSON-LD `Article`：headline / description / inLanguage / articleSection / wordCount / about / datePublished / dateModified / image / **author（@id, @type, name, url, jobTitle, sameAsを5件フルで入れる。名前とurlだけの省略形にしない）** / publisher / mainEntityOfPage。author.sameAsの5件は `https://x.com/m316jp2`, `https://note.com/m316jp2`, `https://withonline.jp/authors/9miIK`, `https://women-ai-initiative.jp/media/posts/miyazaki_award`, `https://shueisha.online/list/persons/698d552bb5762297e9000000`（**twitter.comではなくx.com**）。
- [ ] JSON-LD `BreadcrumbList`。
- [ ] 本文末尾に「Xでシェア」ボタン（`<p class="article-share">`）。
- [ ] 著者アイコン画像は `alt="宮崎真理"`（`alt=""` にしない）。
- [ ] `articles/feed.xml` に新しい `<item>` を先頭に追加し、`lastBuildDate` も更新する。
- [ ] `articles/index.html` に記事カードを追加し、JSON-LD `CollectionPage.mainEntity.itemListElement` にも追加して `numberOfItems` を更新する。
- [ ] `sitemap.xml` に新しいURLを追加し、既存ページの `lastmod` も実際の更新日に合わせる。
- [ ] `index.html` の「生成AIと暮らしの話」プレビュー（3件）を最新3本に差し替える（放置すると古い記事のまま止まる）。
- [ ] 公開後は `python3 scripts/check_site.py` を実行し、リンク切れ・JSON-LD構文エラーが無いことを確認する。
