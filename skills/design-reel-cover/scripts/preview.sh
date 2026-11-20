#!/usr/bin/env bash
# Generates the review views of a 1080x1920 cover:
#   <name>-zones.png   full cover with the profile's 3:4 crop, the Reels interface zones and the composition margins
#   <name>-grid.png    row of 3 3:4 tiles as in the profile (optional neighbors)
#   <name>-mini.png    tile at ~120 px wide, the real size on a phone
# Usage: preview.sh <cover.png> <output_dir> [left_neighbor.png] [right_neighbor.png]
# Exits 2 on a missing file or ffmpeg, 1 if the cover is not 1080x1920.
set -euo pipefail
usage="Usage: preview.sh <cover.png> <output_dir> [left_neighbor.png] [right_neighbor.png]"
case "${1:-}" in -h|--help) echo "$usage"; exit 0;; esac
[ $# -ge 2 ] || { echo "$usage" >&2; exit 2; }
for tool in ffmpeg ffprobe; do command -v "$tool" >/dev/null || { echo "$tool is not installed: this script needs it." >&2; exit 2; }; done
cover="$1"; out="$2"; left="${3:-}"; right="${4:-}"
for f in "$cover" ${left:+"$left"} ${right:+"$right"}; do [ -f "$f" ] || { echo "Image not found: $f" >&2; exit 2; }; done
size="$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0:s=x "$cover" 2>/dev/null || true)"
[ "$size" = "1080x1920" ] || { echo "The cover must be 1080x1920 and $cover is ${size:-not a readable image}: render it at that size." >&2; exit 1; }
mkdir -p "$out"
name="$(basename "${cover%.*}")"
# The zone figures of the skill, on the 1080x1920 canvas. This block is their only source: "Instagram specifications"
# in SKILL.md and the guides of assets/cover-example.html repeat these numbers and must match them.
GRID_TOP=240; GRID_BOTTOM=1680      # the profile grid shows the central 3:4 (1080x1440), drawn in blue
UI_TOP=210                          # Reels viewer: top bar down to this y, drawn in red
UI_BOTTOM=1400                      # Reels viewer: bottom block (user, caption, buttons) from this y at its tallest
UI_COL_X=945; UI_COL_TOP=1095; UI_COL_BOTTOM=1850   # Reels viewer: button column from this x to the right edge
MARGIN=60                           # composition margin on each side, drawn in white
ffmpeg -v error -y -i "$cover" -vf "\
drawbox=x=0:y=0:w=1080:h=$GRID_TOP:color=black@0.55:t=fill,\
drawbox=x=0:y=$GRID_BOTTOM:w=1080:h=$((1920-GRID_BOTTOM)):color=black@0.55:t=fill,\
drawbox=x=0:y=$((GRID_TOP-2)):w=1080:h=4:color=0x4F8CFF:t=fill,\
drawbox=x=0:y=$((GRID_BOTTOM-2)):w=1080:h=4:color=0x4F8CFF:t=fill,\
drawbox=x=0:y=$((UI_TOP-1)):w=1080:h=3:color=red@0.8:t=fill,\
drawbox=x=0:y=$UI_BOTTOM:w=1080:h=3:color=red@0.8:t=fill,\
drawbox=x=$UI_COL_X:y=$UI_COL_TOP:w=$((1080-UI_COL_X)):h=$((UI_COL_BOTTOM-UI_COL_TOP)):color=red@0.8:t=3,\
drawbox=x=$MARGIN:y=0:w=2:h=1920:color=white@0.6:t=fill,\
drawbox=x=$((1080-MARGIN-2)):y=0:w=2:h=1920:color=white@0.6:t=fill" "$out/$name-zones.png"
tile() { ffmpeg -v error -y -i "$1" -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,crop=1080:$((GRID_BOTTOM-GRID_TOP)):0:$GRID_TOP,scale=360:480" "$2"; }
tile "$cover" "$out/.t_c.png"
if [ -n "$left" ]; then tile "$left" "$out/.t_l.png"; else ffmpeg -v error -y -f lavfi -i color=c=0x232730:s=360x480 -frames:v 1 "$out/.t_l.png"; fi
if [ -n "$right" ]; then tile "$right" "$out/.t_r.png"; else ffmpeg -v error -y -f lavfi -i color=c=0x232730:s=360x480 -frames:v 1 "$out/.t_r.png"; fi
ffmpeg -v error -y -i "$out/.t_l.png" -i "$out/.t_c.png" -i "$out/.t_r.png" -filter_complex \
  "[0]pad=364:480:0:0:white[a];[1]pad=364:480:0:0:white[b];[a][b][2]hstack=3,pad=1108:500:10:10:white" "$out/$name-grid.png"
ffmpeg -v error -y -i "$out/.t_c.png" -vf scale=120:160 "$out/$name-mini.png"
rm -f "$out"/.t_?.png
echo "$out/$name-zones.png"; echo "$out/$name-grid.png"; echo "$out/$name-mini.png"
