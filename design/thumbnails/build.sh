#!/bin/bash
# 記事・note・OGPのサムネイルを書き出す（Google Chromeが必要）
set -euo pipefail
cd "$(dirname "$0")"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
category="${1:-articles}"
case "$category" in
  articles|og) size="1200,630" ;;
  note) size="1280,670" ;;
  *) echo "使い方: bash design/thumbnails/build.sh [articles|note|og]" >&2; exit 1 ;;
esac
output_dir="../exports/$category"
mkdir -p "$output_dir"
for source_file in "$category"/*.html; do
  file_name="${source_file##*/}"
  [ "$file_name" = "template.html" ] && continue
  output_file="$output_dir/${file_name%.html}.png"
  "$CHROME" --headless --disable-gpu --hide-scrollbars \
    --force-device-scale-factor=2 --window-size="$size" \
    --virtual-time-budget=4000 --screenshot="$output_file" \
    "file://$PWD/$source_file" 2>/dev/null
  echo "$output_file"
done
