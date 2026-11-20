#!/usr/bin/env bash
# Detects shot cuts inside already prepared b-roll clips (frames from the next shot of a recap that slip in).
# Usage: check-clips.sh <folder-or-files...>   A folder contributes its .mp4, .mov, .m4v, .mkv and .webm files.
# Lists the clips with an internal cut. Exit code 1 if a clip has a cut, cannot be read or no clip was found.
set -uo pipefail
if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then sed -n '2,4p' "$0" | sed 's/^# //'; [ $# -eq 0 ] && exit 2 || exit 0; fi
shopt -s nullglob nocaseglob
files=()
for a in "$@"; do
  if [ -d "$a" ]; then files+=("$a"/*.mp4 "$a"/*.mov "$a"/*.m4v "$a"/*.mkv "$a"/*.webm); else files+=("$a"); fi
done
if [ ${#files[@]} -eq 0 ]; then echo "check-clips: no video files found in: $*" >&2; exit 1; fi
bad=0; checked=0
for f in "${files[@]}"; do
  if ! log=$(ffmpeg -nostdin -nostats -v info -i "$f" -vf "scdet=threshold=12" -an -f null - 2>&1); then
    echo "UNREADABLE $(basename "$f")"; bad=1; continue
  fi
  if ! printf '%s\n' "$log" | grep -q "frame= *[1-9]"; then echo "UNREADABLE $(basename "$f") (no video frames)"; bad=1; continue; fi
  checked=$((checked+1))
  r=$(printf '%s\n' "$log" | grep -o "lavfi.scd.time: [0-9.]*" | tr '\n' ' ')
  if [ -n "$r" ]; then echo "CUT $(basename "$f") -> $r"; bad=1; fi
done
[ $bad = 0 ] && echo "no internal cuts in $checked clips"
exit $bad
