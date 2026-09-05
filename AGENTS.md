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
