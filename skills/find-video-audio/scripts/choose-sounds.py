#!/usr/bin/env python3
"""Page for the user to listen to and approve a piece's sounds and music before the visual test.

Usage: python3 choose-sounds.py <candidates_dir> ["<title>"]
Reads <candidates_dir>/sounds.json: a list with one row per moment of the layer map, like this:
  {"clip": "03", "time": "1.9 s", "moment": "Price appears", "on_screen": "what happens on screen at that instant",
   "spoken": "the sentence or word the creator says at that instant", "purpose": "what the sound has to convey",
   "favorite": "sfx/till-drawer.wav", "reason": "why it is the pick", "signature": false,
   "options": [{"file": "sfx/till-drawer.wav", "note": "Till drawer with bell, from the library, CC0"}]}
"clip" is a string and unique (the page and the server match rows by it). "on_screen", "spoken" and "purpose" are
required: with them the user judges whether the sound fits. "file" and "favorite" are paths relative to
<candidates_dir>: effects in sfx/, music beds in music/ (a row for the music has "music/<file>" options). Rows with
"signature": true are fixed brand sounds: they are shown to be heard in context, with a single option.

The page's own texts are the LABELS below, in English. To show the page in the user's language, write
<candidates_dir>/labels.json with the keys to replace (any subset of LABELS, plus "lang" for the page language).

Writes <candidates_dir>/choose-sounds.html. For the choice to be saved automatically as "chosen" in sounds.json,
serve it with
  python3 <skills>/analyze-video/scripts/serve-choice-page.py <candidates_dir> 8767 sounds.json choose-sounds.html
The default title is the name of the piece folder (two levels above <candidates_dir>).
"""
import html, json, os, sys

LABELS = {
    "lang": "en",
    "heading": "Choose sounds",
    "intro": "Each moment says what is on screen, what is said and what the sound is for, so you can judge whether it "
             "fits. My pick comes preselected. Listen and change any you are not convinced by; from the local link "
             "every selection saves itself. The ones marked as signature are the brand's fixed sounds: they are here "
             "for you to hear, there is no need to choose them. The final level relative to the voice is set in the "
             "mix and you will hear it in the review render.",
    "pick": "My pick",
    "signature": "(brand signature)",
    "on_screen": "On screen",
    "spoken": "Spoken",
    "purpose": "Purpose",
    "copy": "Copy choice",
    "autosave": "Your choice saves itself when you select",
    "saved": "Saved",
    "not_saved": "Could not save",
    "not_saved_copy": "Could not save: use the copy button",
}

if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"): print(__doc__.strip()); sys.exit(0)
if len(sys.argv) < 2: print(__doc__.strip(), file=sys.stderr); sys.exit(2)
HERE = os.path.dirname(os.path.abspath(__file__))
cdir = sys.argv[1]
title = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(os.path.abspath(os.path.join(cdir, "../..")))

def load(name, required):
    path = os.path.join(cdir, name)
    if not os.path.exists(path):
        if required: sys.exit(f"Missing {path}")
        return None
    try: return json.load(open(path, encoding="utf-8"))
    except ValueError as e: sys.exit(f"{path} is not valid JSON: {e}")

rows = load("sounds.json", True)
if not isinstance(rows, list) or not rows: sys.exit("sounds.json has no rows: it must be a list with one row per moment")
labels = dict(LABELS)
custom = load("labels.json", False)
if custom is not None:
    unknown = sorted(set(custom) - set(LABELS)) if isinstance(custom, dict) else ["(not an object)"]
    if unknown: sys.exit(f"labels.json: unknown keys {', '.join(unknown)}. Valid keys: {', '.join(LABELS)}")
    labels.update({k: str(v) for k, v in custom.items()})
esc = {k: html.escape(v) for k, v in labels.items()}

sections, seen = [], set()
for n, f in enumerate(rows, 1):
    clip = f.get("clip") if isinstance(f, dict) else None
    if not isinstance(clip, str) or not clip:
        sys.exit(f"Row {n}: \"clip\" must be a non-empty string (write \"03\", not 3): the server matches rows by it")
    if clip in seen: sys.exit(f"Row {clip}: \"clip\" is repeated")
    seen.add(clip)
    for k in ("time", "moment", "on_screen", "spoken", "purpose"):
        if not f.get(k): sys.exit(f"Row {clip}: missing \"{k}\" (when it plays, what is on screen, what is said and what the sound is for)")
    options = f.get("options") or []
    if not options: sys.exit(f"Row {clip}: no \"options\"")
    files = [o.get("file") for o in options]
    selected = f.get("chosen") or f.get("favorite")
    if f.get("favorite") and f["favorite"] not in files: sys.exit(f"Row {clip}: the favorite {f['favorite']} is not among its options")
    cards = []
    for o in options:
        a = o.get("file")
        if not a: sys.exit(f"Row {clip}: an option has no \"file\"")
        if os.path.isabs(a) or ".." in a.split("/") or not os.path.isfile(os.path.join(cdir, a)):
            sys.exit(f"Row {clip}: missing {a} (paths are relative to {cdir}: sfx/<file> or music/<file>)")
        fav = a == f.get("favorite")
        cards.append(f'<label class="card{" fav" if fav else ""}"><span><input type="radio" name="c{html.escape(clip)}" value="{html.escape(a)}"'
                     f'{" checked" if a == selected else ""}> {html.escape(a)}</span>{"<em>" + esc["pick"] + "</em>" if fav and not f.get("signature") else ""}'
                     f'<audio src="{html.escape(a)}" controls preload="none"></audio><small>{html.escape(o.get("note", ""))}</small></label>')
    signature = f' <span class="signature">{esc["signature"]}</span>' if f.get("signature") else ""
    use = (f'<dl class="use"><dt>{esc["on_screen"]}</dt><dd>{html.escape(f["on_screen"])}</dd><dt>{esc["spoken"]}</dt><dd>{html.escape(f["spoken"])}</dd>'
           f'<dt>{esc["purpose"]}</dt><dd>{html.escape(f["purpose"])}</dd></dl>')
    reason = use + (f'<p class="reason">{esc["pick"]}: {html.escape(f["reason"])}</p>' if f.get("reason") else "")
    sections.append(f'<section data-clip="{html.escape(clip)}"><h2><b>{html.escape(f["time"])}</b>{html.escape(f["moment"])}{signature}</h2>{reason}'
                    f'<div class="row">{"".join(cards)}</div></section>')

page = open(os.path.join(HERE, "../assets/choose-sounds.html"), encoding="utf-8").read()
values = {"TITLE": html.escape(title), "SECTIONS": "\n".join(sections), "LANG": esc["lang"], "HEADING": esc["heading"],
          "INTRO": esc["intro"], "COPY": esc["copy"],
          "LABELS_JSON": json.dumps({k: labels[k] for k in ("autosave", "saved", "not_saved", "not_saved_copy")}, ensure_ascii=False).replace("</", "<\\/")}
for k, v in values.items(): page = page.replace("{{" + k + "}}", v)
out = os.path.join(cdir, "choose-sounds.html")
open(out, "w", encoding="utf-8").write(page)
print(out)
