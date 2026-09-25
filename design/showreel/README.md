# ショーリール 2026（15秒）

履歴書・ポートフォリオ用のモーショングラフィックス映像。miyazakimari.com の配色（#f2c40f / #141413 / #f7f6f2）と書体（Space Grotesk・Zen Kaku Gothic New）、`assets/images/` の公開画像だけで構成しています。書体は書き出し環境に左右されないよう `fonts/` に同梱（SIL Open Font License、ライセンス文も同梱）。

- 完成版: `miyazakimari-showreel-2026.mp4`（1920×1080・60fps・H.264＋AAC、BGM・効果音は `score.py` で合成したオリジナル）
- サムネイル: `poster.png`（最終カット）

## 構成（120BPM・1小節＝2秒でカットと音を同期）

| 秒 | シーン | 内容 |
|---|---|---|
| 0–2 | 01 INTRO | 黄色の線が「×」に折れ、「AI × 家事」が×の裏から出る。×が回転して画面を黄色で満たす |
| 2–4 | 02 MESSAGE | 「生成AIで、暮らしをラクに。」を1文字ずつ立ち上げ、「ラクに」を反転ハイライト。回転バッジ |
| 4–6 | 03 PROFILE | アーチ窓からポートレート、氏名、ローマ字のスクランブル、肩書きピル。黄色の円で次へ |
| 6–8 | 04 BOOK | 『AI×家事』の3D書籍が回転しながら着地。1000日間・60の活用例をカウントアップ |
| 8–10 | 05 MEDIA | 16分音符でテレビ局・媒体名を8カット。続けて「50+」 |
| 10–12 | 06 AWARD | スラット状のワイプで受賞写真、ライフ・イノベーター賞に光沢、受賞スタンプ |
| 12–15 | 07 CONTACT | 実績写真のモザイクから中央の「×」へダイブし、氏名・仕事内容・URLで締める |

## 書き出し

```sh
npm i playwright-core          # 初回のみ（design/showreel で）
python3 score.py               # BGM・効果音 → design/exports/showreel/audio.wav
node render.mjs stills 3.2 7   # 指定秒の静止画を確認
node render.mjs video          # 本番（各コマ4サブフレームを合成したモーションブラー付き）
```

`CHROME`（Chromiumのパス）、`FFMPEG`（libx264入りのffmpeg）、`WORKERS`（並列数）は環境変数で指定できます。出力先は `design/exports/showreel/`（Git対象外）。ブラウザで `showreel.html?play` を開くと実時間でプレビュー、`render(秒)` で任意のコマを表示できます。
