#!/usr/bin/env bash
# Summarizes a video or audio file: codec, size, fps, duration, color space and whether it is HDR.
# Usage: probe-media.sh <file> [...]
set -euo pipefail
if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then sed -n '2,3p' "$0" | sed 's/^# //'; [ $# -eq 0 ] && exit 2 || exit 0; fi
for f in "$@"; do
  echo "== $f"
  ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,r_frame_rate,pix_fmt,color_primaries,color_transfer,color_space -of default=nw=1 "$f" 2>/dev/null | sed 's/^/  /'
  ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels -of default=nw=1 "$f" 2>/dev/null | sed 's/^/  audio: /'
  ffprobe -v error -show_entries format=duration,size,bit_rate -of default=nw=1 "$f" | sed 's/^/  /'
  trc=$(ffprobe -v error -select_streams v:0 -show_entries stream=color_transfer -of default=nw=1:nk=1 "$f" 2>/dev/null || true)
  prim=$(ffprobe -v error -select_streams v:0 -show_entries stream=color_primaries -of default=nw=1:nk=1 "$f" 2>/dev/null || true)
  case "$trc$prim" in
    *arib-std-b67*|*smpte2084*|*bt2020*) echo "  HDR: yes (render with --sdr; ask for the next recording to be made with HDR video turned off in the camera settings)";;
    *) echo "  HDR: no";;
  esac
done
