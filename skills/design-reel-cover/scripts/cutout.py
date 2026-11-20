"""Cuts the subject out of a frame or an image with rembg.

Usage (uv sets up rembg in a temporary environment; each model is downloaded once to rembg's model folder, ~/.u2net unless U2NET_HOME points elsewhere):
  uv run --python 3.11 --with "rembg[cpu]" python cutout.py <input.png> <output.png> [--model <name>]

--model: the rembg model. Default birefnet-portrait, made for a person (the creator in a frame). For an object, a
product, food or any subject that is not a person, use isnet-general-use. Any other rembg model name is accepted.
Writes a PNG with transparency. Exits 2 on a usage error or a missing input, 1 if the model cannot be loaded.
"""
import os, sys

args = sys.argv[1:]
if args and args[0] in ("-h", "--help"):
    print(__doc__.strip()); sys.exit(0)
model = "birefnet-portrait"
if "--model" in args:
    i = args.index("--model")
    if i + 1 >= len(args):
        print("--model needs a name, for example isnet-general-use", file=sys.stderr); sys.exit(2)
    model = args[i + 1]; del args[i:i + 2]
if len(args) != 2:
    print(__doc__.strip(), file=sys.stderr); sys.exit(2)
src, dst = args
if not os.path.isfile(src):
    print("Input not found: %s" % src, file=sys.stderr); sys.exit(2)

from PIL import Image
from rembg import new_session, remove

try:
    session = new_session(model)
except Exception as e:
    print("Could not load the rembg model \"%s\" (unknown name, or no network for its first download): %s" % (model, e), file=sys.stderr); sys.exit(1)
result = remove(Image.open(src).convert("RGB"), session=session, post_process_mask=True)
os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
result.save(dst)
print(dst, result.size, "model", model)
