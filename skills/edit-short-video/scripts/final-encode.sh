#!/usr/bin/env bash
# Writes the deliverable from a HyperFrames render in a single encode: speed (pitch intact), loudness and the export preset.
# Preset: H.264 High, 30 fps, 8-bit 4:2:0, BT.709, about 11 Mbps (peak 20), keyframe every second, AAC 256 kbps at 48 kHz,
# moov at the front. Loudness: two loudnorm passes to the target, true peak target -1.5 dBTP, measured on the sped-up audio.
# Usage: final-encode.sh <render.mp4> <output.mp4> [--speed 1.1] [--target -14]     (--speed 1 keeps the normal speed)
# Then measures the output with loudness.sh. Exit code: 0 written and in range, 1 failed or out of range, 2 wrong arguments.
set -uo pipefail
usage() { sed -n '2,6p' "$0" | sed 's/^# //'; }
case "${1:-}" in -h|--help) usage; exit 0;; esac
if [ $# -lt 2 ]; then usage; exit 2; fi
in="$1"; out="$2"; shift 2
speed=1; target=-14
while [ $# -gt 0 ]; do
  case "$1" in
    --speed|--target) [ $# -ge 2 ] || { echo "final-encode: $1 needs a value" >&2; exit 2; }
      if [ "$1" = --speed ]; then speed="$2"; else target="$2"; fi; shift;;
    *) echo "final-encode: unknown argument $1" >&2; usage >&2; exit 2;;
  esac
  shift
done
[[ "$speed" =~ ^(0\.[5-9][0-9]*|1(\.[0-9]+)?|2(\.0+)?)$ ]] || { echo "final-encode: --speed must be between 0.5 and 2 (1.1 is 110 %), got '$speed'" >&2; exit 2; }
[[ "$target" =~ ^-[0-9]+(\.[0-9]+)?$ ]] || { echo "final-encode: --target must be a negative number of LUFS, got '$target'" >&2; exit 2; }
[ -f "$in" ] || { echo "final-encode: file not found: $in" >&2; exit 1; }
[ "$in" != "$out" ] || { echo "final-encode: the output must be a different file from the render" >&2; exit 2; }
here="$(cd "$(dirname "$0")" && pwd)"
norm="loudnorm=I=$target:TP=-1.5:LRA=11"
m=$(ffmpeg -nostdin -hide_banner -nostats -i "$in" -vn -af "atempo=$speed,$norm:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
[ -n "$m" ] || { echo "final-encode: no audio could be measured in $in" >&2; exit 1; }
measured=$(python3 -I -c '
import sys, json; d = json.loads(sys.argv[1])
print("measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true" % (d["input_i"], d["input_tp"], d["input_lra"], d["input_thresh"], d["target_offset"]))' "$m") || exit 1
mkdir -p "$(dirname "$out")"
ffmpeg -nostdin -y -hide_banner -loglevel error -i "$in" \
  -filter_complex "[0:v]setpts=PTS/$speed,fps=30[v];[0:a]atempo=$speed,$norm:$measured,aresample=48000[a]" -map "[v]" -map "[a]" \
  -c:v libx264 -profile:v high -preset slow -b:v 11M -maxrate 20M -bufsize 22M -g 30 -pix_fmt yuv420p \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -c:a aac -b:a 256k -ar 48000 -ac 2 -movflags +faststart "$out" || { echo "final-encode: the encode failed" >&2; exit 1; }
echo "== written: $out (speed $speed)"
"$here/loudness.sh" "$out" --target "$target"
