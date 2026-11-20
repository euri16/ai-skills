#!/usr/bin/env python3
"""Joins images into a single sheet, side by side, each under its label, to present versions to the user.

Usage: python3 side-by-side.py <output.png> "<label>" <image> ["<label>" <image> ...] [--height 1200]
Each image is scaled to the same height (default 1200 px) and keeps its proportions. The label goes above it, as
written: put in it what the user has to know ("Real photo", "A · generated", in the user's language).
Needs Pillow (python3 -m pip install --user Pillow). Exits 2 on a usage error or a missing image.
"""
import os, sys

def die(msg, code=2): print(msg, file=sys.stderr); sys.exit(code)
args = sys.argv[1:]
if args and args[0] in ("-h", "--help"): print(__doc__.strip()); sys.exit(0)
height = 1200
if "--height" in args:
    i = args.index("--height")
    try: height = int(args[i + 1])
    except (IndexError, ValueError): die("--height needs a whole number of pixels")
    del args[i:i + 2]
if len(args) < 3 or len(args) % 2 == 0 or height < 100: die(__doc__.strip())
try: from PIL import Image, ImageDraw, ImageFont
except ImportError: die("Pillow is missing for this python3: python3 -m pip install --user Pillow")
out, pairs = args[0], list(zip(args[1::2], args[2::2]))
for _, p in pairs:
    if not os.path.isfile(p): die("Image not found: %s" % p)

BG, INK, PAD, SIZE = (21, 23, 28), (243, 241, 236), 30, 44     # neutral dark sheet, light text
def font():
    for path in ("/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf"):
        if os.path.exists(path):
            try: return ImageFont.truetype(path, SIZE)
            except OSError: pass
    try: return ImageFont.load_default(SIZE)       # Pillow 10.1 or later
    except TypeError: return None
FONT = font()
def label_image(text, width):
    """The label as an image of the column's width; without a scalable font, the small built-in one is enlarged."""
    if FONT:
        im = Image.new("RGB", (width, SIZE + 20), BG); d = ImageDraw.Draw(im)
        while d.textlength(text, font=FONT) > width and len(text) > 4: text = text[:-2].rstrip() + "…"
        d.text((0, 4), text, font=FONT, fill=INK); return im
    small = ImageFont.load_default(); w = max(1, width // 4)
    im = Image.new("RGB", (w, (SIZE + 20) // 4), BG); ImageDraw.Draw(im).text((0, 2), text, font=small, fill=INK)
    return im.resize((width, SIZE + 20), Image.NEAREST)

cols = []
for text, p in pairs:
    try: im = Image.open(p).convert("RGBA")
    except Exception as e: die("Could not open %s as an image: %s" % (p, e), 1)
    w = max(1, round(im.width * height / im.height)); im = im.resize((w, height), Image.LANCZOS)
    flat = Image.new("RGB", im.size, BG); flat.paste(im, mask=im.split()[3])     # transparent areas on the sheet color
    cols.append((label_image(text, w), flat))
total_w = sum(c[1].width for c in cols) + PAD * (len(cols) + 1)
sheet = Image.new("RGB", (total_w, height + SIZE + 20 + PAD * 3), BG)
x = PAD
for lab, im in cols:
    sheet.paste(lab, (x, PAD)); sheet.paste(im, (x, PAD * 2 + SIZE + 20)); x += im.width + PAD
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
sheet.save(out)
print(out, sheet.size)
