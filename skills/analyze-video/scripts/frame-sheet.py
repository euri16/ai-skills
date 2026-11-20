#!/usr/bin/env python3
"""Frame sheet: every frame of a short stretch, in order and with its time, to find an exact gesture.

Usage: uv run -q --with pillow python frame-sheet.py <video> <output.png> <start> <duration> [--fps 6] [--crop x,y,w,h] [--width 270] [--cols 9]

  --fps       frames per second to sample (6 to go through a take; 12.5 for the exact instant)
  --crop      area in pixels of the original video (for example the face and the hand) to see the detail
  --width     width of each cell in the sheet
  --cols      cells per row
Each cell carries the time in seconds of the original video. To extract the chosen frame at full resolution:
  ffmpeg -ss <t> -i <video> -frames:v 1 <output.png>
Colors: CONTACT_SHEET_BG and CONTACT_SHEET_ACCENT (hex, same variables as frames.sh); the defaults are a neutral palette.
"""
import json, os, subprocess, sys

a = sys.argv[1:]
if len(a) < 4 or "-h" in a or "--help" in a: sys.exit(__doc__)
from PIL import Image, ImageDraw, ImageFont

def opt(name, default):
    if name in a:
        i = a.index(name); v = a[i + 1]; del a[i:i + 2]; return v
    return default
def rgb(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
fps = float(opt("--fps", "6")); crop = opt("--crop", None); width = int(opt("--width", "270")); cols = int(opt("--cols", "9"))
video, output, start, dur = a[0], a[1], float(a[2]), float(a[3])
bg, accent = rgb(os.environ.get("CONTACT_SHEET_BG", "#15171C")), rgb(os.environ.get("CONTACT_SHEET_ACCENT", "#4F8CFF"))

st = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                         "-of", "json", video], text=True))["streams"][0]
w0, h0 = st["width"], st["height"]
x, y, w, h = map(int, crop.split(",")) if crop else (0, 0, w0, h0)
height = round(width * h / w)
vf = f"fps={fps},crop={w}:{h}:{x}:{y},scale={width}:{height}"
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-t", str(dur), "-i", video, "-vf", vf, "-f", "rawvideo",
                      "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
n = len(raw) // (width * height * 3)
if not n: sys.exit("no frames in that stretch")
rows = (n + cols - 1) // cols
sheet = Image.new("RGB", (cols * width, rows * height), bg)
d = ImageDraw.Draw(sheet)
try: f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", max(14, width // 11))
except OSError: f = ImageFont.load_default()
for k in range(n):
    im = Image.frombytes("RGB", (width, height), raw[k * width * height * 3:(k + 1) * width * height * 3])
    cx, cy = (k % cols) * width, (k // cols) * height
    sheet.paste(im, (cx, cy))
    t = f"{start + k / fps:.2f}s"
    d.rectangle((cx + 4, cy + 4, cx + 10 + d.textlength(t, font=f), cy + 8 + getattr(f, "size", 12)), fill=accent)
    d.text((cx + 7, cy + 5), t, fill=bg, font=f)
sheet.save(output)
print(f"{output}: {n} frames from {start:.2f} to {start + (n - 1) / fps:.2f} s")
