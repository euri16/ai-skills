#!/usr/bin/env bash
# Lists the instant of each hit of a multi-hit sound (keys, tiles, clicks) and writes them next to the audio as JSON,
# so an animation can be synced to them.
# Usage: hit-times.sh <audio> [--noise -35] [--gap 0.03]
#   --noise   level in dB under which the sound counts as the silence between hits (default -35)
#   --gap     shortest silence, in seconds, that separates two hits (default 0.03)
# Writes <audio without extension>.hits.json: {"file": "<name>", "duration": <s>, "hits": [<seconds from the start>, ...]}.
# A hit is the instant the sound rises above the noise level after a silence. Exits 1 if no hit is found.
set -euo pipefail
usage() { sed -n '2,8p' "$0" | sed 's/^# //'; }
case "${1:-}" in -h|--help) usage; exit 0;; "") usage >&2; exit 2;; esac
for tool in ffmpeg ffprobe python3; do command -v "$tool" >/dev/null || { echo "$tool is not installed: this script needs it." >&2; exit 2; }; done
f="$1"; shift
noise=-35; gap=0.03
while [ $# -gt 0 ]; do
  case "$1" in
    --noise|--gap) [ $# -ge 2 ] || { echo "$1 needs a value." >&2; exit 2; };;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2;;
  esac
  case "$1" in --noise) noise="$2";; --gap) gap="$2";; esac
  shift 2
done
[ -f "$f" ] || { echo "Audio not found: $f" >&2; exit 2; }
dur=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$f" 2>/dev/null || true)
case "$dur" in ''|*[!0-9.]*) echo "ffprobe could not read $f as audio." >&2; exit 1;; esac
log=$(ffmpeg -hide_banner -nostats -i "$f" -af "silencedetect=noise=${noise}dB:d=${gap}" -f null - 2>&1) || { echo "ffmpeg could not analyze $f (check --noise and --gap)." >&2; exit 1; }
out="${f%.*}.hits.json"
printf '%s\n' "$log" | python3 -I -c '
import json, os, re, sys
f, dur, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
log = sys.stdin.read()
starts = [float(x) for x in re.findall(r"silence_start: (-?[0-9.]+)", log)]
ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", log)]
hits = [] if (starts and starts[0] <= 0.005) else [0.0]      # sound from the first sample: a hit at 0
hits += [e for e in ends if e < dur - 0.005]
if starts and starts[0] <= 0.005 and len(starts) == 1 and not hits: sys.exit("No hit found in %s: the file is silent at this --noise level." % f)
if not hits: sys.exit("No hit found in %s." % f)
hits = [round(h, 3) for h in hits]
json.dump({"file": os.path.basename(f), "duration": round(dur, 3), "hits": hits}, open(out, "w"), indent=1)
print("%d hits: %s" % (len(hits), ", ".join("%.3f" % h for h in hits)))
print(out)' "$f" "$dur" "$out"
