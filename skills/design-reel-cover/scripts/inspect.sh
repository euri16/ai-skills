#!/usr/bin/env bash
# Cuts the cover into 6 crops at real size (540x640, 2 columns x 3 rows) to review it up close.
# Seen whole, a 1080x1920 is shown scaled down and hides dirty edges, blends and loose fragments.
# Usage: inspect.sh <cover.png> <output_dir>
# Exits 2 on a missing cover or ffmpeg, 1 if the cover is not 1080x1920.
set -euo pipefail
usage="Usage: inspect.sh <cover.png> <output_dir>"
case "${1:-}" in -h|--help) echo "$usage"; exit 0;; esac
[ $# -ge 2 ] || { echo "$usage" >&2; exit 2; }
for tool in ffmpeg ffprobe; do command -v "$tool" >/dev/null || { echo "$tool is not installed: this script needs it." >&2; exit 2; }; done
cover="$1"; out="$2"
[ -f "$cover" ] || { echo "Cover not found: $cover" >&2; exit 2; }
size="$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0:s=x "$cover" 2>/dev/null || true)"
[ "$size" = "1080x1920" ] || { echo "The cover must be 1080x1920 and $cover is ${size:-not a readable image}: render it at that size." >&2; exit 1; }
mkdir -p "$out"
name="$(basename "${cover%.*}")"
for r in 0 1 2; do for c in 0 1; do
  ffmpeg -v error -y -i "$cover" -vf "crop=540:640:$((c*540)):$((r*640))" "$out/$name-detail-$((r+1))$((c+1)).png"
  echo "$out/$name-detail-$((r+1))$((c+1)).png"
done; done
