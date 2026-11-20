#!/usr/bin/env bash
# Joins the cover options into a single image, side by side, to present them to the user.
# Each column shows the option's letter and name, the full cover and how it looks in the grid.
# Usage: compare.sh <output.png> "<A · name>" <a.png> "<B · name>" <b.png> [...]
# Brand values (neutral defaults; set them from the workspace's brand-guide/visual-identity.md):
#   BRAND_DIR        brand folder with assets/fonts/fonts.css (default: ./brand-guide from the current directory)
#   COMPARE_BG       sheet background color (default #15171C)
#   COMPARE_INK      text and outline color (default #F3F1EC)
#   COMPARE_FONT     label font family declared in fonts.css (default Helvetica)
#   COMPARE_GRID_LABEL  caption above the grid tile (default "In the grid"; use the user's language)
# Exits 2 on a usage error or a missing image, 1 if the render fails. A missing fonts.css is only a warning.
set -euo pipefail
usage='Usage: compare.sh <output.png> "<A · name>" <a.png> "<B · name>" <b.png> [...]'
case "${1:-}" in -h|--help) echo "$usage"; exit 0;; esac
[ $# -ge 3 ] && [ $(( $# % 2 )) -eq 1 ] || { echo "$usage" >&2; exit 2; }
here="$(cd "$(dirname "$0")" && pwd)"
out="$1"; shift
brand_dir="${BRAND_DIR:-$PWD/brand-guide}"
fonts_css="$(cd "$brand_dir" 2>/dev/null && pwd)/assets/fonts/fonts.css" || fonts_css=""
fonts_link=""
if [ -f "$fonts_css" ]; then
  fonts_link="<link rel=\"stylesheet\" href=\"file://$(python3 -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1]))' "$fonts_css")\">"
else
  echo "warning: fonts.css not found under $brand_dir/assets/fonts; labels fall back to Helvetica" >&2
fi
# Labels and captions are text, not HTML: escape them.
esc() { printf '%s' "$1" | sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g'; }
bg="${COMPARE_BG:-#15171C}"; ink="${COMPARE_INK:-#F3F1EC}"; font="${COMPARE_FONT:-Helvetica}"
grid_label="$(esc "${COMPARE_GRID_LABEL:-In the grid}")"
dir="$(mktemp -d)"; trap 'rm -rf "$dir"' EXIT
cols=""; n=0
while [ "$#" -ge 2 ]; do
  label="$(esc "$1")"; img="$2"; shift 2; n=$((n+1))
  [ -f "$img" ] || { echo "Image not found: $img" >&2; exit 2; }
  cp "$img" "$dir/o$n.png"
  cols="$cols<div class=c><h2>$label</h2><img class=full src=o$n.png><p>$grid_label</p><div class=tile style=\"background-image:url(o$n.png)\"></div></div>"
done
w=$(( n * 600 + 60 )); h=1420
cat > "$dir/compare.html" <<HTML
<!doctype html><meta charset="utf-8">
$fonts_link
<style>
body{margin:0;padding:30px;background:$bg;display:flex;gap:60px;font-family:"$font",Helvetica,Arial;color:$ink}
.c{width:540px}h2{margin:0 0 16px;font:900 40px "$font",Helvetica,Arial}
.full{width:540px;height:960px;display:block;border-radius:18px;box-shadow:0 0 0 4px $ink}
p{margin:22px 0 10px;font-weight:700;font-size:26px}
.tile{width:180px;height:240px;background-size:180px 320px;background-position:0 -40px;border-radius:4px;box-shadow:0 0 0 3px $ink}
</style>$cols
HTML
"$here/render.sh" "$dir/compare.html" "$out" "$w" "$h" >/dev/null
echo "$out"
