#!/usr/bin/env bash
# Extracts frames from a render at the given times and joins them into a sheet to review them like a designer.
# Usage: review-frames.sh <video.mp4> <out_dir> <t1> [t2 ...]
# Writes in <out_dir> (for a piece, social/<piece>/edit/tests/<name>): f_<t>.png at full size and sheet.png with all of them side by side.
set -euo pipefail
case "${1:-}" in -h|--help) sed -n '2,4p' "$0" | sed 's/^# //'; exit 0;; esac
if [ $# -lt 3 ]; then sed -n '2,4p' "$0" | sed 's/^# //'; exit 2; fi
v="$1"; dir="$2"; shift 2
[[ "$dir" =~ ^[0-9]+(\.[0-9]+)?$ ]] && { echo "review-frames: the second argument is the output folder, got the number '$dir'" >&2; exit 2; }
[ -f "$v" ] || { echo "review-frames: file not found: $v" >&2; exit 1; }
for t in "$@"; do
  [[ "$t" =~ ^[0-9]+(\.[0-9]+)?$ ]] || { echo "review-frames: '$t' is not a time in seconds (usage: <video> <out_dir> <t1> [t2 ...])" >&2; exit 2; }
done
mkdir -p "$dir"
inputs=(); n=0; filter=""
for t in "$@"; do
  ffmpeg -nostdin -v error -y -ss "$t" -i "$v" -frames:v 1 "$dir/f_$t.png"
  [ -s "$dir/f_$t.png" ] || { echo "review-frames: no frame at $t s (is it past the end of the video?)" >&2; exit 1; }
  inputs+=(-i "$dir/f_$t.png"); filter="$filter[$n:v]scale=360:-2[s$n];"; n=$((n+1))
done
if [ "$n" -eq 1 ]; then
  ffmpeg -nostdin -v error -y "${inputs[@]}" -filter_complex "${filter%;}" -map "[s0]" "$dir/sheet.png"
else
  join=""; for ((i=0;i<n;i++)); do join="$join[s$i]"; done
  ffmpeg -nostdin -v error -y "${inputs[@]}" -filter_complex "${filter}${join}hstack=inputs=$n" "$dir/sheet.png"
fi
echo "$dir/sheet.png"; echo "full-size frames in $dir"
