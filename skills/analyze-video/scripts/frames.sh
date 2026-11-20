#!/usr/bin/env bash
# Extracts candidate frames from a video and builds a contact sheet with the time of each one.
# Usage: frames.sh <video> <output_dir> [t1 t2 ...]   (seconds; without times, takes 12 evenly spread samples)
# The sheet is rendered with headless Chrome: $CHROME_BIN, or the default macOS Google Chrome path.
# Without Chrome or without a video stream it stops before extracting anything and says why.
# Colors: $CONTACT_SHEET_BG and $CONTACT_SHEET_ACCENT (hex); the defaults are a neutral palette.
set -euo pipefail
if [ "$#" -lt 2 ]; then sed -n '2,6p' "$0" | sed 's/^# \{0,1\}//'; exit 1; fi
video="$1"; out="$2"; shift 2
chrome="${CHROME_BIN:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
bg="${CONTACT_SHEET_BG:-#15171C}"; accent="${CONTACT_SHEET_ACCENT:-#4F8CFF}"
if [ ! -f "$video" ]; then echo "frames.sh: \"$video\" does not exist" >&2; exit 1; fi
if [ ! -x "$chrome" ]; then
  echo "frames.sh: Chrome not found at \"$chrome\": install Google Chrome or set CHROME_BIN to a Chrome or Chromium binary" >&2; exit 1
fi
if [ -z "$(ffprobe -v error -select_streams V -show_entries stream=index -of csv=p=0 "$video")" ]; then
  echo "frames.sh: \"$video\" has no video stream, so there are no frames to extract" >&2; exit 1
fi
mkdir -p "$out"
dur="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$video")"
if [ "$#" -eq 0 ]; then
  set -- $(python3 -c "d=float('$dur');n=12;print(' '.join(f'{d*(i+0.5)/n:.2f}' for i in range(n)))")
fi
cells=""
for t in "$@"; do
  f="$out/f_${t}.png"
  ffmpeg -v error -y -ss "$t" -i "$video" -frames:v 1 "$f"
  ffmpeg -v error -y -i "$f" -vf scale=360:-2 "$out/s_${t}.jpg"
  cells="$cells<figure><img src=\"s_${t}.jpg\"><figcaption>${t}s</figcaption></figure>"
done
n="$#"; cols=$(( n < 6 ? n : 6 )); rows=$(( (n + cols - 1) / cols ))
w=$(( cols * 380 + 20 )); h=$(( rows * 660 + 20 ))
cat > "$out/contact.html" <<HTML
<!doctype html><meta charset="utf-8"><style>
body{margin:0;padding:10px;background:$bg;display:grid;grid-template-columns:repeat($cols,360px);gap:20px;font:700 34px Helvetica,Arial}
figure{margin:0;position:relative}img{width:360px;display:block;border-radius:10px}
figcaption{position:absolute;left:10px;top:10px;background:$accent;color:$bg;padding:4px 14px;border-radius:999px}
</style>$cells
HTML
abs="$(cd "$out" && pwd)"; log="$abs/.chrome.log"
rm -f "$abs/contact.png"
"$chrome" --headless=new --disable-gpu --allow-file-access-from-files \
  --hide-scrollbars --force-device-scale-factor=1 --window-size="$w,$h" --virtual-time-budget=4000 \
  --screenshot="$abs/contact.png" "file://$(python3 -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1]))' "$abs/contact.html")" >"$log" 2>&1 || true
if [ ! -s "$abs/contact.png" ]; then
  echo "frames.sh: Chrome did not render the contact sheet ($chrome). Its last output:" >&2; tail -n 5 "$log" >&2; rm -f "$log"; exit 1
fi
rm -f "$log"
echo "duration: ${dur}s"
echo "sheet: $out/contact.png"
echo "full-resolution frames: $out/f_<t>.png"
