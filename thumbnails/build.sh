#!/bin/bash
# 記事サムネイルを PNG に書き出す（要 Google Chrome）
set -e
cd "$(dirname "$0")"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for f in [0-9][0-9].html; do
  out="${f%.html}.png"
  "$CHROME" --headless --disable-gpu --hide-scrollbars \
    --force-device-scale-factor=2 --window-size=1200,630 \
    --virtual-time-budget=4000 --screenshot="$out" "file://$PWD/$f" 2>/dev/null
  echo "  $out"
done
