# miyazakimari.com

宮崎真理のポートフォリオサイト。HTML・CSS・JavaScriptで構成した静的サイトです。

## ファイルの場所

| 場所 | 内容 |
|---|---|
| `index.html` | トップページ。スタイルとJavaScriptもこの中 |
| `book/` | 著書紹介ページ |
| `articles/` | 公開記事。記事ごとに `index.html` と `cover.png` |
| `assets/images/` | 公開画像。書籍・人物・イベント・受賞・書店・ランキング別 |
| `design/thumbnails/` | 記事・note・OGPのサムネイルHTMLと書き出しスクリプト |
| `design/exports/` | サムネイルの書き出し先（Git対象外） |
| `drafts/portfolio/`・`drafts/note/` | 未公開の原稿（Git対象外） |
| `archive/source-images/` | 再編集用の元写真・資料画像（Git対象外） |
| `screenshots/` | 日付入りのサイト更新記録 |
| `docs/` | 整理・変更の記録 |
| `scripts/check_site.py` | 内部リンク・画像参照の確認 |

`favicon.svg`・`favicon-32.png`・`apple-touch-icon.png`・`og-image.jpg` は、共通アイコンとシェア画像としてルートに置いています。`CNAME`・`.nojekyll`・`robots.txt`・`sitemap.xml`・`llms.txt` は公開用の設定です。

## 確認と制作

プロジェクトフォルダで次のコマンドを実行します。

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

ブラウザで `http://127.0.0.1:8765/` を開きます。サーバーはCtrl+Cで終了します。

```sh
python3 scripts/check_site.py
bash design/thumbnails/build.sh articles
bash design/thumbnails/build.sh note
bash design/thumbnails/build.sh og
```

サムネイルの書き出しにはGoogle Chromeが必要です。生成先は `design/exports/`。公開記事に使う画像は、確認後に対象の `articles/<記事名>/cover.png` へコピーします。

大きな更新では、変更前後のスクリーンショットを `screenshots/YYYY-MM-DD/` に保存し、タイトルとファイル名の両方に日付を入れます。同日の別更新は名前を分けて残します。

[2026-09-05 ファイル整理の詳細](docs/2026-09-05-file-organization.md) · [2026-09-05 画面の比較](screenshots/2026-09-05/README.md)
