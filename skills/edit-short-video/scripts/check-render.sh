#!/usr/bin/env bash
# Checks a render frame by frame before showing it to the user:
#  - vertical white strip (HyperFrames capture defect with huge images), searched in every column of every frame
# Usage: check-render.sh <video.mp4>
# A strip is a column that is light and flat from 21 % to 73 % of the height and at least 60 levels lighter than the
# median column. Prints the frames with one (time and x): look at them, because a plain light vertical bar that belongs
# to the design reads the same. Exit code 1 if it finds one, or if the file cannot be read.
set -euo pipefail
if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then sed -n '2,7p' "$0" | sed 's/^# //'; [ $# -eq 0 ] && exit 2 || exit 0; fi
v="$1"
[ -f "$v" ] || { echo "check-render: file not found: $v" >&2; exit 1; }
info=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of csv=p=0 "$v") || { echo "check-render: cannot read $v" >&2; exit 1; }
[ -n "$info" ] || { echo "check-render: no video stream in $v" >&2; exit 1; }
ffmpeg -nostdin -v error -i "$v" -vf "format=gray" -f rawvideo - | uv run -q --python 3.11 --with numpy python -c '
import sys, numpy as np
w, h, rate = sys.argv[1].split(",")[:3]
w, h = int(w), int(h); num, den = rate.split("/"); fps = float(num) / float(den)
y0, y1 = round(h * 0.21), round(h * 0.73)       # the band between the top and bottom interface zones
frames, bad = 0, []
while True:
    buf = sys.stdin.buffer.read(w * h)
    if len(buf) < w * h:
        break
    a = np.frombuffer(buf, np.uint8).reshape(h, w)[y0:y1].astype(np.float32)
    mean, std = a.mean(axis=0), a.std(axis=0)
    hit = np.where((mean > 200) & (std < 35) & (mean - np.median(mean) > 60))[0]
    if len(hit):
        bad.append((frames, int(hit[0]), int(hit[-1])))
    frames += 1
if not frames:
    sys.exit("check-render: no frames could be decoded")
for n, x0, x1 in bad[:20]:
    print("STRIP at %.2f s (frame %d), x %d to %d" % (n / fps, n, x0, x1))
if len(bad) > 20:
    print("... and %d more frames" % (len(bad) - 20))
print("%d frames of %dx%d checked, frames with a strip: %d" % (frames, w, h, len(bad)))
sys.exit(1 if bad else 0)' "$info"
