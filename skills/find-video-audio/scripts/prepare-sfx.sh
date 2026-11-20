#!/usr/bin/env bash
# Prepares an SFX: trims leading and trailing silence, converts to 48 kHz WAV and normalizes the sample peak to -3 dBFS (or to the --peak value).
# Usage: prepare-sfx.sh <input> <output.wav> [--peak -3] [--mono]
# The peak is the sample peak that ffmpeg's volumedetect measures, not a true peak. Exits 1 when the input has no audio left after trimming.
set -euo pipefail
usage() { sed -n '2,4p' "$0" | sed 's/^# //'; }
case "${1:-}" in -h|--help) usage; exit 0;; esac
[ $# -ge 2 ] || { usage >&2; exit 2; }
for tool in ffmpeg ffprobe; do command -v "$tool" >/dev/null || { echo "$tool is not installed: this script needs it." >&2; exit 2; }; done
in="$1"; out="$2"; shift 2
peak=-3; mono=()
while [ $# -gt 0 ]; do
  case "$1" in
    --peak) [ $# -ge 2 ] || { echo "--peak needs a value." >&2; exit 2; }; peak="$2"; shift;;
    --mono) mono=(-ac 1);;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2;;
  esac
  shift
done
[ -f "$in" ] || { echo "Input not found: $in" >&2; exit 2; }
awk "BEGIN{exit !(\"$peak\" ~ /^-?[0-9]+(\\.[0-9]+)?\$/ && $peak+0 <= 0)}" || { echo "--peak takes a level in dBFS of 0 or less, not \"$peak\"." >&2; exit 2; }
tmpd="$(mktemp -d)"; trap 'rm -rf "$tmpd"' EXIT
tmp="$tmpd/trimmed.wav"
ffmpeg -y -hide_banner -loglevel error -i "$in" -af "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.02,areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05,areverse" -ar 48000 ${mono[@]+"${mono[@]}"} "$tmp" \
  || { echo "ffmpeg could not read $in as audio." >&2; exit 1; }
mx=$(ffmpeg -hide_banner -nostats -i "$tmp" -af volumedetect -f null - 2>&1 | grep -o "max_volume: [-0-9.]*" | awk '{print $2}' || true)
case "$mx" in ""|-91.0) echo "No audio left after trimming the silence of $in: the file is silent or below -50 dB." >&2; exit 1;; esac
gain=$(awk "BEGIN{printf \"%.2f\", $peak - ($mx)}")
mkdir -p "$(dirname "$out")"
ffmpeg -y -hide_banner -loglevel error -i "$tmp" -af "volume=${gain}dB" "$out"
dur=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$out")
echo "$out  duration ${dur}s  sample peak ${peak} dBFS (gain ${gain} dB)"
