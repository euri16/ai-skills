#!/usr/bin/env python3
"""Sheet to review the cuts of the takes: for each sentence, four frames of the face.

Usage: check-cuts.py <recording_dir> <takes_dir> <output_dir> [chosen|favorite]
Columns: 0.12 s before the in point · in point · last frame of the cut (0.02 s before the out point) · 0.12 s after the
out point. Each frame is cropped to the face area cuts.py wrote in the row ("face"), with margin around it; a row without
it shows the center of the frame.
A cut is right when the in point looks the same as the settled moment before the voice (without the face changing
from rest to speaking) and the out point does not show the face relaxing, looking away or the body moving.
Leaves check-<n>.png (11 sentences per sheet) in <output_dir>.
"""
import json, os, subprocess, sys, tempfile
if len(sys.argv) < 4: sys.exit(__doc__)
rec, tdir, out = sys.argv[1:4]
which = sys.argv[4] if len(sys.argv) > 4 else "chosen"
os.makedirs(out, exist_ok=True)
sentences = json.load(open(os.path.join(tdir, "sentences.json")))
tmp = tempfile.mkdtemp()
rows = []

def crop(zone):
    """ffmpeg crop of the face area (fractions of the frame) widened by a third of its size on each side."""
    x0, y0, x1, y1 = zone
    mx, my = (x1 - x0) / 3, (y1 - y0) / 3
    x0, y0, x1, y1 = max(0, x0 - mx), max(0, y0 - my), min(1, x1 + mx), min(1, y1 + my)
    return f"crop=iw*{x1 - x0:.4f}:ih*{y1 - y0:.4f}:iw*{x0:.4f}:ih*{y0:.4f}"

for f in sentences:
    lab = f.get(which) or f.get("favorite")
    if not lab or lab not in f.get("cuts", {}): continue
    a, b = f["cuts"][lab]
    imgs = []
    for i, t in enumerate([a - 0.12, a, b - 0.02, b + 0.12]):
        o = os.path.join(tmp, f"{f['clip']}-{i}.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0, t):.3f}", "-i", os.path.join(rec, f["file"]), "-frames:v", "1",
                        "-vf", f"{crop(f.get('face') or (0.34, 0.36, 0.66, 0.54))},scale=220:220:force_original_aspect_ratio=decrease,"
                               "pad=220:220:(ow-iw)/2:(oh-ih)/2", o], check=True)
        imgs.append(o)
    row = os.path.join(tmp, f"row-{f['clip']}.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + sum([["-i", x] for x in imgs], []) + ["-filter_complex", "hstack=inputs=4", row], check=True)
    rows.append(row)
    print(f["clip"], lab, f"{a:.2f}-{b:.2f}")
for n in range(0, len(rows), 11):
    group = rows[n:n + 11]
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + sum([["-i", x] for x in group], [])
                   + ["-filter_complex", f"vstack=inputs={len(group)}" if len(group) > 1 else "null",
                      os.path.join(out, f"check-{n // 11 + 1}.png")], check=True)
