#!/usr/bin/env bash
# Detects scene cuts and prints the start, end and center (a representative time) of each shot, tab-separated.
# Usage: scenes.sh <video> [threshold]   (threshold 0-1, default 0.3; lower = more cuts)
# A file without a video stream (audio only, or audio with cover art) has no shots: it prints nothing and exits 0.
set -euo pipefail
if [ "$#" -lt 1 ]; then sed -n '2,4p' "$0" | sed 's/^# \{0,1\}//'; exit 1; fi
video="$1"; thr="${2:-0.3}"
if [ ! -f "$video" ]; then echo "scenes.sh: \"$video\" does not exist" >&2; exit 1; fi
if [ -z "$(ffprobe -v error -select_streams V -show_entries stream=index -of csv=p=0 "$video")" ]; then exit 0; fi
dur="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$video")"
cuts="$(ffmpeg -hide_banner -nostats -i "$video" -an -vf "select='gt(scene,$thr)',showinfo" -f null - 2>&1 \
  | sed -n 's/.*pts_time:\([0-9.]*\).*/\1/p')"
python3 - "$dur" $cuts <<'PY'
import sys
dur = float(sys.argv[1]); cuts = [float(c) for c in sys.argv[2:]]
edges = [0.0] + [c for c in cuts if 0.4 < c < dur - 0.4] + [dur]
shots = [(a, b) for a, b in zip(edges, edges[1:]) if b - a >= 0.4]
for a, b in shots:
    print(f"{a:.2f}\t{b:.2f}\t{(a + b) / 2:.2f}")
PY
