#!/usr/bin/env bash
# Full analysis of a video: metadata, transcription, shots and contact sheet.
# Usage: analyze.sh <video|audio> <output_dir> [language] [vocabulary]
#   language and vocabulary work as in transcribe.sh ($WHISPER_LANGUAGE, $WHISPER_VOCABULARY).
# Leaves in <output_dir>: analysis.md, transcript.{txt,srt,json}, words.json and frames/contact.png
# An audio file (no video stream) gets the metadata and the transcript only: no shots, no frames.
set -euo pipefail
if [ "$#" -lt 2 ]; then sed -n '2,6p' "$0" | sed 's/^# \{0,1\}//'; exit 1; fi
here="$(cd "$(dirname "$0")" && pwd)"
video="$1"; out="$2"; lang="${3:-${WHISPER_LANGUAGE:-auto}}"; vocab="${4:-}"
mkdir -p "$out"; out="$(cd "$out" && pwd)"
meta="$(ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height,r_frame_rate -of compact=p=0 "$video")"
dur="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$video")"
"$here/transcribe.sh" "$video" "$out" "$lang" "$vocab"
if [ -z "$(ffprobe -v error -select_streams V -show_entries stream=index -of csv=p=0 "$video")" ]; then
  {
    echo "# Analysis of $(basename "$video")"
    echo
    echo "## Metadata"
    echo
    echo '```'
    echo "$meta"
    echo '```'
    echo
    echo "Audio only: no shots and no frames."
    echo
    echo "## Transcript"
    echo
    echo '```'
    cat "$out/transcript.txt"
    echo '```'
  } > "$out/analysis.md"
  echo "$out/analysis.md"
  exit 0
fi
shots="$("$here/scenes.sh" "$video")"
n="$(printf '%s\n' "$shots" | grep -c .)"
# One frame per shot and one every ~3 s inside long shots. At most 24.
times="$(python3 - "$dur" "$n" <<PY
import sys
dur, n = float(sys.argv[1]), int(sys.argv[2])
shots = [l.split("\t") for l in """$shots""".strip().splitlines()]
mids = []
for a, b, m in ((float(x) for x in s) for s in shots):
    # Long shots (video to camera): one frame every ~3 s instead of only the center.
    k = max(1, round((b - a) / 3))
    mids += [a + (b - a) * (i + 0.5) / k for i in range(k)]
if len(mids) > 24:
    k = len(mids) / 24
    mids = [mids[int(i * k)] for i in range(24)]
print(" ".join(f"{t:.1f}" for t in mids))
PY
)"
"$here/frames.sh" "$video" "$out/frames" $times >/dev/null
{
  echo "# Analysis of $(basename "$video")"
  echo
  echo "## Metadata"
  echo
  echo '```'
  echo "$meta"
  echo '```'
  echo
  echo "## Detected shots ($n)"
  echo
  echo "| Start | End |"
  echo "|---|---|"
  printf '%s\n' "$shots" | awk -F'\t' '{printf "| %ss | %ss |\n", $1, $2}'
  echo
  echo "## Transcript"
  echo
  echo '```'
  cat "$out/transcript.txt"
  echo '```'
  echo
  echo "## Frames"
  echo
  echo "Contact sheet: \`frames/contact.png\` (times: $times)."
  echo "Full-resolution frames: \`frames/f_<t>.png\`."
} > "$out/analysis.md"
echo "$out/analysis.md"
echo "$out/frames/contact.png"
