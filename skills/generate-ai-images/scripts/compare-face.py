#!/usr/bin/env python3
"""Compares the face in a generated photo with the face in the real photo it starts from.

Usage: uv run -q --python 3.11 --with numpy --with "opencv-python-headless<5" --with pillow python compare-face.py <real> <generated> <output.png> [--threshold 14]

<real> is the exact base image that was attached to the generation (the reduced copy, not the camera original), so both
have the same framing. Detects the face in the real photo (with a margin for hair and chin), resizes the generated one to
the same size and measures the mean per-pixel difference (0 to 255) in that area, after compensating a global change in
brightness and contrast (the AI often retouches the tone). Leaves in <output.png> the real face and the generated one side
by side, at full size, to review them by eye. Exits with code 1 if the difference exceeds the threshold (the face changed),
if no face is found or if the two images have different proportions (resizing would stretch the face and the number
would mean nothing), and with code 2 on a usage error or a missing file. The number does not replace the review by eye: a
face can pass the threshold and still change a feature.
"""
import os, sys

def die(msg, code=2): print(msg, file=sys.stderr); sys.exit(code)
args = sys.argv[1:]
if "-h" in args or "--help" in args: print(__doc__.strip()); sys.exit(0)
threshold = 14.0
if "--threshold" in args:
    i = args.index("--threshold")
    try: threshold = float(args[i + 1])
    except (IndexError, ValueError): die("--threshold needs a number")
    del args[i:i + 2]
if len(args) != 3: die(__doc__.strip())
real_p, gen_p, out_p = args
for p in (real_p, gen_p):
    if not os.path.isfile(p): die("Image not found: %s" % p)

from PIL import Image

real_im, gen_im = Image.open(real_p).convert("RGB"), Image.open(gen_p).convert("RGB")
ratio_real, ratio_gen = real_im.width / real_im.height, gen_im.width / gen_im.height
if abs(ratio_real - ratio_gen) / ratio_real > 0.01:
    die("the images have different proportions (real %dx%d, generated %dx%d): compare against the exact base that was attached, "
        "or regenerate asking for the same aspect ratio" % (real_im.width, real_im.height, gen_im.width, gen_im.height), 1)

import cv2
import numpy as np

real = np.array(real_im)
gen = np.array(gen_im.resize((real.shape[1], real.shape[0]), Image.LANCZOS))
cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
faces = cascade.detectMultiScale(cv2.cvtColor(real, cv2.COLOR_RGB2GRAY), 1.1, 5, minSize=(real.shape[1] // 10,) * 2)
if not len(faces):
    die("no face detected in the real photo: the comparison could not be measured, review by eye", 1)
x, y, w, h = max(faces, key=lambda r: r[2] * r[3])
x0, y0 = max(0, int(x - 0.15 * w)), max(0, int(y - 0.35 * h)); x1, y1 = min(real.shape[1], int(x + 1.15 * w)), min(real.shape[0], int(y + 1.15 * h))
a = real[y0:y1, x0:x1].astype(np.float32); b = gen[y0:y1, x0:x1].astype(np.float32)
b_norm = (b - b.mean()) / (b.std() + 1e-6) * a.std() + a.mean()          # compensates a global tone retouch
diff = float(np.abs(a - b_norm).mean())
side_by_side = np.hstack([real[y0:y1, x0:x1], np.full((y1 - y0, 12, 3), 255, np.uint8), gen[y0:y1, x0:x1]])
Image.fromarray(side_by_side).save(out_p)
ok = diff <= threshold
print(f"face difference: {diff:.1f} (threshold {threshold:g}) -> {'same' if ok else 'CHANGED'}; side-by-side crop in {out_p}")
sys.exit(0 if ok else 1)
