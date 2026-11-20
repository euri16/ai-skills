#!/usr/bin/env python3
"""Space map: checks, before building, that every graphic fits in the real framing without covering the face or the subtitles.

Usage: uv run -q --python 3.11 --with numpy --with "opencv-python-headless<5" --with "rembg[cpu]" python space-map.py <space.json> <out_dir> [--card-bg "#15171C"]

space.json (coordinates on the 1080x1920 canvas, boxes as [x, y, width, height]; video paths relative to the folder of
space.json):
{"beats": [
  {"name": "B1 oven timer", "video": "../source/recording/X.MP4", "t": 2.0,
   "vf": "crop=1382:2458:173:309,scale=1080:1920",          # the same crop and scale as the chosen shot (optional)
   "subtitle": [200, 1284, 680, 106],                        # subtitle box for that beat, or null
   "graphics": [{"name": "timer", "box": [240, 1420, 600, 240], "min_text_px": 36}],   # min_text_px is required
   "card": {"edge": 1150},                                   # only in split view: y of the top edge of the camera card
   "face": false}                                            # only when the creator is not in the frame (full-screen visual)
]}
A beat of a visual video, which has no recording to take a frame from, has no "video" and "t": it gives "image", a 1080x1920 frame of the composition
taken with `hyperframes snapshot`, and "face": false, for example
  {"name": "S2 figure", "image": "../tests/visual-test/frame-02.png", "face": false, "subtitle": null,
   "graphics": [{"name": "headline", "box": [84, 420, 912, 250], "min_text_px": 92}]}
Every block of the scene is declared as a graphic, with its box as it is seen in that frame.

Detects the face in each frame (with a margin for hair and chin) and marks: face in red, subtitle in yellow, graphics in
blue, safe zone in gray. A beat fails if:
- a graphic touches the face or the subtitle, its smallest text is below 36 px or is not declared, it leaves the safe
  zone (x 60 to 1020, y 210 to 1680) or enters the button column (x 945 to 1080, y 1095 to 1850);
- the subtitle covers the face, leaves x 60 to 1020, starts above y 210 or ends below y 1400;
- the frame cannot be read or the face is not detected (unless the beat says "face": false): a beat that could not be
  seen is not a pass. Choose another instant of the beat where the creator faces the camera. An "image" that is not
  1080x1920, a beat with both "image" and "video" or with neither, and an "image" beat without "face": false or with
  no graphic and no subtitle declared (nothing to check) fail the same way.
With "card", the top of the hair is measured with the creator's real silhouette (rembg, birefnet-portrait model, the same
cutout that sticks out in the video) and the frame is drawn as it will come out: above the edge only the background
(--card-bg, the brand's dark background color) and the cut-out head. It also fails if a graphic goes below the edge (the
card would end up behind the b-roll) or if the edge does not pass at eyebrow height (30 px tolerance). The subtitle sits at
the seam by default: it fails if it goes below the edge, if there are fewer than 40 px between it and the hair or if it
is not centered between the graphic and the hair (more than 24 px difference). With "card": {"edge": N, "subtitle":
"below-face"} (variant 2b) the subtitle sits on the card under the chin and only the general subtitle checks apply.
Leaves space-map.png (one column per beat) and space-map.md with the result of each check. Exit code 1 if a beat fails.
"""
import argparse, json, os, re, subprocess, sys

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("spec", help="space.json")
ap.add_argument("out", help="output folder for space-map.png and space-map.md")
ap.add_argument("--card-bg", default="#15171C",
                help="background color drawn above the card edge, as a 6-digit hex; the default #15171C is a neutral "
                     "dark gray, pass the dark background of the workspace's brand-guide/visual-identity.md")
args = ap.parse_args()
if not re.fullmatch(r"#?[0-9a-fA-F]{6}", args.card_bg):
    ap.error(f"--card-bg must be a 6-digit hex color such as #15171C, got '{args.card_bg}'")

import cv2, numpy as np

spec, out = args.spec, args.out; os.makedirs(out, exist_ok=True)
hexbg = args.card_bg.lstrip("#")
card_bg = tuple(int(hexbg[i:i + 2], 16) for i in (4, 2, 0))          # BGR for OpenCV
SUBTITLE_BGR, GRAPHIC_BGR = (40, 200, 240), (255, 140, 79)             # overlay colors: yellow #F0C828, blue #4F8CFF
SUBTITLE_FLOOR = 1400                                                  # the subtitle box never ends below this y
BUTTONS = [945, 1095, 135, 755]
base = os.path.dirname(os.path.abspath(spec))
beats = json.load(open(spec)).get("beats") or sys.exit("space-map: space.json has no beats")
cas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")   # OpenCV 4

_session = None
def silhouette(img):
    """Alpha of the creator's silhouette in the frame (0 to 255)."""
    global _session
    from PIL import Image
    from rembg import new_session, remove
    if _session is None: _session = new_session("birefnet-portrait")
    return np.array(remove(Image.fromarray(img[:, :, ::-1]), session=_session, post_process_mask=True))[:, :, 3]

def overlaps(a, b):
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah

cols, report, failed = [], ["# Space map", "", "| Beat | Check | Result |", "|---|---|---|"], 0
for b in beats:
    name, bad = b["name"], []                       # bad: every problem of this beat
    def row(check, problems, ok):
        bad.extend(problems)
        report.append(f"| {name} | {check} | {'; '.join(problems) if problems else ok} |")
    graphics, sub, card = b.get("graphics", []), b.get("subtitle"), b.get("card")
    problem = None
    if ("image" in b) == ("video" in b):
        problem = "the beat needs exactly one of \"video\" (with \"t\") or \"image\": nothing was checked"
    elif "image" in b and b.get("face", True):
        problem = "an \"image\" beat is a frame of a visual video: declare \"face\": false"
    elif "image" in b and not graphics and not sub:
        problem = "an \"image\" beat that declares no graphic and no subtitle has nothing to check"
    elif "image" in b:
        path = os.path.join(base, b["image"])
        size = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                               "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
        if size != "1080,1920":
            problem = f"{b['image']} is not a readable 1080x1920 frame (got {size or 'nothing'}): nothing was checked"
        else:
            shot = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-frames:v", "1", "-vf", "format=bgr24",
                                   "-f", "rawvideo", "-"], capture_output=True)
    else:
        vf = (b.get("vf") + "," if b.get("vf") else "") + "scale=1080:1920,format=bgr24"
        shot = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(b["t"]), "-i", os.path.join(base, b["video"]), "-frames:v", "1",
                               "-vf", vf, "-f", "rawvideo", "-"], capture_output=True)
    if not problem and (shot.returncode or len(shot.stdout) != 1920 * 1080 * 3):
        problem = f"could not read a frame of {b.get('video') or b['image']}" + (f" at {b['t']} s" if "video" in b else "") + ": nothing was checked"
    if problem:
        row("frame", [problem], "")
        failed += 1
        blank = np.zeros((640, 360, 3), np.uint8); cv2.putText(blank, "no frame", (40, 320), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cols.append(blank); continue
    img = np.frombuffer(shot.stdout, np.uint8).reshape(1920, 1080, 3).copy()
    face = None
    if b.get("face", True):
        faces = cas.detectMultiScale(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 1.1, 5, minSize=(150, 150))
        if len(faces):
            x, y, w, h = max(faces, key=lambda r: r[2] * r[3])
            face = [int(x - 0.15 * w), int(y - 0.4 * h), int(1.3 * w), int(1.65 * h)]   # hair above, chin below
        else:
            row("face", ["not detected: the face and card checks did not run; use another instant of the beat, "
                         "or \"face\": false if the creator is not in the frame"], "")
    elif card:
        row("card", ["a card beat needs the creator in the frame: remove \"face\": false"], "")
    below_face = bool(card) and card.get("subtitle", "seam") == "below-face"
    if card and card.get("subtitle", "seam") not in ("seam", "below-face"):
        row("card", [f"unknown \"subtitle\" value {card['subtitle']!r}: use \"seam\" or \"below-face\""], "")
    if card and face:
        edge = card["edge"]; brows = face[1] + int(0.412 * face[3])   # eyebrow line: about 0.28 h below the top edge of the detected face
        alpha = silhouette(img)
        x0, x1 = max(0, face[0]), min(1080, face[0] + face[2])     # head columns, so a raised hand is not counted
        rows = np.where((alpha[:, x0:x1] > 128).sum(1) > 6)[0]
        if not len(rows):
            row("card", ["silhouette not detected: the card checks did not run"], "")
        else:
            hair, problems = int(rows[0]), []
            on_top = graphics + ([{"name": "subtitle", "box": sub}] if sub and not below_face else [])
            for g in on_top:
                if g["box"][1] + g["box"][3] > edge: problems.append(f"{g['name']} goes below the card edge (y {edge}): the card ends up behind")
            if sub and not below_face:
                gap = hair - (sub[1] + sub[3])
                if gap < 40: problems.append(f"only {gap} px between the subtitle and the hair")
                above_g = [g["box"][1] + g["box"][3] for g in graphics if g["box"][1] + g["box"][3] <= sub[1]]
                if above_g and abs((sub[1] - max(above_g)) - gap) > 24:
                    problems.append(f"subtitle not centered in the seam: {sub[1] - max(above_g)} px above it and {gap} px below it")
            if abs(edge - brows) > 30: problems.append(f"the edge does not pass at the eyebrows: it is {edge - brows:+d} px from their line (y {brows})")
            row(f"card (edge {edge}, sticks out {edge - hair} px)", problems, "well placed")
            background = img.copy(); background[:] = card_bg
            above = np.zeros(img.shape[:2], bool); above[:edge] = True
            img[above & (alpha < 128)] = background[above & (alpha < 128)]
            cv2.line(img, (0, edge), (1080, edge), (255, 255, 255), 4)
    layer = img.copy()
    cv2.rectangle(layer, (60, 210), (1020, 1680), (150, 150, 150), 3); cv2.rectangle(layer, (945, 1095), (1080, 1850), (150, 150, 150), -1)
    if face: cv2.rectangle(layer, (face[0], face[1]), (face[0] + face[2], face[1] + face[3]), (40, 40, 230), -1)
    if sub: cv2.rectangle(layer, (sub[0], sub[1]), (sub[0] + sub[2], sub[1] + sub[3]), SUBTITLE_BGR, -1)
    for g in graphics:
        x, y, w, h = g["box"]; cv2.rectangle(layer, (x, y), (x + w, y + h), GRAPHIC_BGR, -1)
    img = cv2.addWeighted(layer, 0.45, img, 0.55, 0)
    for g in graphics:
        x, y, w, h = g["box"]; cv2.rectangle(img, (x, y), (x + w, y + h), GRAPHIC_BGR, 6)
        problems = []
        if face and overlaps(g["box"], face): problems.append("covers the face")
        if sub and overlaps(g["box"], sub): problems.append("collides with the subtitle")
        if "min_text_px" not in g: problems.append("min_text_px not declared (the smallest text of the graphic, in px on the canvas; 0 if it has no text)")
        elif 0 < g["min_text_px"] < 36: problems.append(f"text of {g['min_text_px']} px (minimum 36)")
        if x < 60 or x + w > 1020 or y < 210 or y + h > 1680: problems.append("leaves the safe zone")
        if overlaps(g["box"], BUTTONS): problems.append("enters the button column")
        row(g["name"], problems, "fits")
    if sub:
        x, y, w, h = sub; problems = []
        if face and (not card or below_face) and overlaps(sub, face): problems.append("covers the face")   # at the seam, subtitle vs. hair is measured above with the real silhouette
        if x < 60 or x + w > 1020: problems.append("leaves the side margins (x 60 to 1020)")
        if y < 210: problems.append("starts above y 210")
        if y + h > SUBTITLE_FLOOR: problems.append(f"ends at y {y + h}, below y {SUBTITLE_FLOOR}")
        row("subtitle", problems, "fits")
    failed += bool(bad)
    cv2.putText(img, name.encode("ascii", "ignore").decode(), (40, 120), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 8)
    cols.append(cv2.resize(img, (360, 640)))
sheet = np.hstack(cols) if len(cols) <= 8 else np.vstack([np.hstack(cols[i:i + 8] + [np.zeros_like(cols[0])] * (8 - len(cols[i:i + 8]))) for i in range(0, len(cols), 8)])
cv2.imwrite(os.path.join(out, "space-map.png"), sheet)
report += ["", f"Beats with problems: {failed} of {len(beats)}." if failed else f"Everything fits ({len(beats)} beats)."]
open(os.path.join(out, "space-map.md"), "w").write("\n".join(report) + "\n")
print("\n".join(report[2:])); sys.exit(1 if failed else 0)
