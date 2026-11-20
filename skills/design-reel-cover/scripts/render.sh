#!/usr/bin/env bash
# Renders an HTML file to PNG with headless Chrome.
# Usage: render.sh <file.html> <output.png> [width] [height] [query]
# optional query, e.g. "guides=1" to draw the crop and interface guides of the cover's HTML.
# CHROME_BIN overrides the browser binary (default: Google Chrome on macOS).
# Exits 2 on a missing HTML file, browser or python3, 1 if Chrome does not write the image.
set -euo pipefail
usage="Usage: render.sh <file.html> <output.png> [width] [height] [query]"
case "${1:-}" in -h|--help) echo "$usage"; exit 0;; esac
[ $# -ge 2 ] || { echo "$usage" >&2; exit 2; }
html="$1"; out="$2"; w="${3:-1080}"; h="${4:-1920}"; q="${5:-}"
chrome="${CHROME_BIN:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
[ -f "$html" ] || { echo "HTML file not found: $html" >&2; exit 2; }
[ -x "$chrome" ] || command -v "$chrome" >/dev/null 2>&1 || { echo "Chrome not found at \"$chrome\": install Google Chrome or export CHROME_BIN=<path to the browser binary>." >&2; exit 2; }
command -v python3 >/dev/null || { echo "python3 is not installed: this script needs it." >&2; exit 2; }
case "$w$h" in *[!0-9]*) echo "width and height are whole numbers of pixels, not \"$w\" and \"$h\"." >&2; exit 2;; esac
abs="$(cd "$(dirname "$html")" && pwd)/$(basename "$html")"
url="file://$(python3 -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1]))' "$abs")"
[ -n "$q" ] && url="$url?$q"
mkdir -p "$(dirname "$out")"
outabs="$(cd "$(dirname "$out")" && pwd)/$(basename "$out")"
rm -f "$outabs"                                    # so an old render does not count as this one
"$chrome" --headless=new --disable-gpu --allow-file-access-from-files --hide-scrollbars \
  --force-device-scale-factor=1 --window-size="$w,$h" --virtual-time-budget=6000 \
  --screenshot="$outabs" "$url" >/dev/null 2>&1 || true
[ -s "$outabs" ] || { echo "render failed: Chrome did not write $outabs (from $abs)" >&2; exit 1; }
echo "$outabs"
