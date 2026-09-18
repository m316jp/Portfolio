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
- [ ] `articles/index.html` の「気になるところから読む」で、新記事を次の4ルートのうち最も自然な1つへ追加する：①まず使ってみたい ②AIと考え、あとから続けたい ③暮らしを自分に合わせたい ④家族・経験・仕事へ広げたい。記事数が増えてルートの意味がぼやける場合は、機械的に追加せず構成を見直す。
- [ ] 新記事本文には、読者が次に持つ疑問に沿った文脈内リンクを1〜2本入れる。リンク数を増やすための不自然な追記はせず、主張を深掘りする既存記事だけを選ぶ。
- [ ] 新記事の末尾に、理由を先に示す「この続きを読む」を2本置く（`.related-question`＋`.related-title`）。長い関連記事一覧や、同じリンクを別の導線で重複表示しない。
- [ ] 新記事から既存記事へつなぐだけでなく、関係が強い既存記事1〜2本から新記事へもリンクを返し、HTML版とMarkdown版をそろえる。更新した既存記事の`dateModified`・表示上の更新日・`sitemap.xml`の`lastmod`も合わせる。
- [ ] `llms.txt` の「読みもの」に新記事を追加し、本人の一次体験と記事固有の発見が分かる説明を付ける。
- [ ] `sitemap.xml` に新しいURLを追加し、既存ページの `lastmod` も実際の更新日に合わせる。
- [ ] `index.html` の「生成AIと暮らしの話」プレビュー（3件）を最新3本に差し替える（放置すると古い記事のまま止まる）。
- [ ] 公開後は `python3 scripts/check_site.py` を実行し、リンク切れ・JSON-LD構文エラーが無いことを確認する。

# 新しいHTMLページ全般（記事に限らず）で必須のもの

- [ ] Google Analytics（`G-1WMFC152MS`）のタグをheadに入れる。過去にトップページ以外の全ページ（記事・書籍・404・privacy）で丸ごと抜けていて、記事へのアクセスがGA4に一切計測されていなかったことがある。新規ページは必ず入っているか確認する。
- [ ] `<meta name="description">` は上記と同じく実文字数で120〜160文字程度（`wc -m`は使わない）。

# メディア実績（プレスカバレッジ）を追加するときのチェックリスト

「〇〇に掲載された／取材された」系の実績を `index.html` の `#media` セクションに追加するとき。

- [ ] リンクは可能な限り配信元（集英社オンライン・ESSE online・with class など）の直リンクを使う。**Yahoo!ニュース等の転載・シンジケーション先のURLは数ヶ月で消えて404になることがある**ので、転載先しか無い場合も配信元の直リンクを優先して探す。既に転載URLしか手元に無いときは、あとで配信元URLが見つかったら差し替えられるようメモを残す。
- [ ] 対応するJSON-LD `NewsArticle`（ItemList内）も追加・更新する。`publisher.name`は実際の配信元名にする（「〇〇 / Yahoo!ニュース」のような転載併記はリンクを直リンクに変えたら外す）。
- [ ] 新しい媒体（今までこのサイトに登場していない媒体名）を追加したときは、Web記事セクションの `<p class="web-media-lead">執筆コラムから取材記事まで、これまでにX媒体・50本以上。</p>` の媒体数（X）を実際の数に更新する。目立たせなくていい実績は、`media-archive`（「その他のメディア実績を見る」の折りたたみ）内に追加すればよい。

# やって裏目に出たこと（繰り返さない）

- 画像`<img>`タグにHTML属性で`width`/`height`（CLS対策）を一括追加したところ、表示が崩れると指摘されすぐ元に戻した。**原因は未調査のまま**。再度やるなら、まずCSS側（`width:100%`だけで`height:auto`が無い、`aspect-ratio`との衝突など）を確認し、1枚だけ試してから全体に広げる。
