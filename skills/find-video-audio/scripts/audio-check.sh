#!/usr/bin/env bash
# Checks audio files: validity, duration, sample peak, mean level, integrated loudness if measurable, leading and trailing silence, and loop join.
# Usage: audio-check.sh <file> [...]
# Exits 1 if any file is missing, broken or empty; the other files are still measured.
set -euo pipefail
usage() { sed -n '2,4p' "$0" | sed 's/^# //'; }
case "${1:-}" in -h|--help) usage; exit 0;; "") usage >&2; exit 2;; esac
for tool in ffmpeg ffprobe python3; do command -v "$tool" >/dev/null || { echo "$tool is not installed: this script needs it." >&2; exit 2; }; done
bad=0
for f in "$@"; do
  echo "== $f"
  if [ ! -f "$f" ]; then echo "  FILE NOT FOUND"; bad=1; continue; fi
  size=$(wc -c < "$f" | tr -d ' ')
  dur=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$f" 2>/dev/null || echo "")
  case "$dur" in ''|*[!0-9.]*) dur="";; esac
  if [ "$size" -lt 2000 ] || [ -z "$dur" ] || awk "BEGIN{exit !($dur <= 0.01)}"; then echo "  BROKEN OR EMPTY FILE (${size} bytes)"; bad=1; continue; fi
  echo "  duration: ${dur}s"
  vd=$(ffmpeg -hide_banner -nostats -i "$f" -af volumedetect -f null - 2>&1 || true)
  mx=$(echo "$vd" | grep -o "max_volume: [-0-9.]*" | awk '{print $2}' || true); mean=$(echo "$vd" | grep -o "mean_volume: [-0-9.]*" | awk '{print $2}' || true)
  echo "  sample peak: ${mx:-?} dBFS   mean level: ${mean:-?} dBFS"
  if awk "BEGIN{exit !($dur >= 1.0)}"; then
    { ffmpeg -hide_banner -nostats -i "$f" -af "loudnorm=I=-14:TP=-1:LRA=11:print_format=json" -f null - 2>&1 || true; } | sed -n '/^{/,/^}/p' | python3 -I -c '
import sys,json
try:
    d=json.load(sys.stdin); print("  integrated loudness: %s LUFS   true peak: %s dBTP" % (d["input_i"], d["input_tp"]))
except Exception: print("  integrated loudness: not measurable")'
  else
    echo "  integrated loudness: not applicable (under 1 s); use sample peak and mean level"
  fi
  sd=$(ffmpeg -hide_banner -nostats -i "$f" -af "silencedetect=noise=-45dB:d=0.05" -f null - 2>&1 || true)
  ss=$(echo "$sd" | grep -o "silence_start: [-0-9.]*" | head -1 | awk '{print $2}' || true)
  se=$(echo "$sd" | grep -o "silence_end: [0-9.]*" | head -1 | awk '{print $2}' || true)
  if [ -n "$ss" ] && awk "BEGIN{exit !($ss < 0.02)}"; then echo "  leading silence: up to ${se:-the end}s (trim if it is an SFX and it exceeds 0.15 s)"; else echo "  leading silence: no"; fi
  rd=$(ffmpeg -hide_banner -nostats -i "$f" -af "areverse,silencedetect=noise=-45dB:d=0.05" -f null - 2>&1 || true)
  rs=$(echo "$rd" | grep -o "silence_start: [-0-9.]*" | head -1 | awk '{print $2}' || true)
  re=$(echo "$rd" | grep -o "silence_end: [0-9.]*" | head -1 | awk '{print $2}' || true)
  if [ -n "$rs" ] && awk "BEGIN{exit !($rs < 0.02)}"; then echo "  trailing silence: ${re:-the whole file}s (trim if it exceeds 0.3 s)"; else echo "  trailing silence: no"; fi
  a=$(ffmpeg -hide_banner -nostats -i "$f" -t 0.1 -af volumedetect -f null - 2>&1 | grep -o "mean_volume: [-0-9.]*" | awk '{print $2}' || true)
  b=$(ffmpeg -hide_banner -nostats -sseof -0.1 -i "$f" -af volumedetect -f null - 2>&1 | grep -o "mean_volume: [-0-9.]*" | awk '{print $2}' || true)
  if [ -z "$a" ] || [ -z "$b" ]; then
    echo "  loop: start/end level not measurable"
  else
    gap=$(awk "BEGIN{d=($a)-($b); if(d<0)d=-d; printf \"%.1f\", d}")
    if awk "BEGIN{exit !($gap <= 6)}"; then verdict="levels join; listen to the join, a level match does not prove a musical one"; else verdict="does not join without a crossfade"; fi
    echo "  loop: first/last 0.1 s at ${a} / ${b} dB, ${gap} dB apart: ${verdict}"
  fi
done
exit $bad
