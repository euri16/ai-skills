#!/usr/bin/env python3
"""Page for the user to choose the best take of each sentence.

Usage: choose-takes.py <recording_dir> <analysis_dir> <output_dir> [title]
- Reads <analysis_dir>/takes.json (from takes.sh).
- If <output_dir>/sentences.json does not exist, writes a draft (one row per file, all takes with voice) and uses it.
  Edit it to assign each row to its script clip, set the decided sentence and remove discarded takes;
  a list [4, 5] in "takes" joins consecutive takes (a sentence split in two with its pause). Run again.
- Leaves a light proxy per take (<clip>-t<n>.mp4) and choose-takes.html in <output_dir>.
- If the row has "cuts" (from cuts.py), each proxy uses that exact cut; otherwise, fixed margins around the voice.
- If the row has "favorite" and "reason" (from score-takes.py), marks it with a label and leaves it selected;
  "chosen", when it already exists, takes precedence over the favorite.
- Every string of the page comes from the template (../assets/choose-takes.html): the labels of each row are its
  <meta name="label-..."> tags, read through labels.py. A take keeps its key "Take N" as the value saved in
  sentences.json and is shown with the template's word for "Take".
"""
import html, json, os, subprocess, sys
if len(sys.argv) < 4: sys.exit(__doc__)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from labels import label, take_name
NO_VOICE = "(no voice or noise)"                       # written by takes.sh
rec, analysis_dir, out = sys.argv[1:4]
title = sys.argv[4] if len(sys.argv) > 4 else os.path.basename(os.path.abspath(os.path.join(out, "../..")))
os.makedirs(out, exist_ok=True)
takes = json.load(open(os.path.join(analysis_dir, "takes.json")))
T = {(x["file"], x["take"]): x for x in takes}
sj = os.path.join(out, "sentences.json")
if not os.path.exists(sj):
    rows = {}
    for x in takes:
        if x["text"] != NO_VOICE:
            rows.setdefault(x["file"], []).append(x)
    draft = [{"clip": f"{i:02d}", "part": "", "sentence": max((t["text"] for t in ts), key=[t["text"] for t in ts].count),
              "file": a, "takes": [t["take"] for t in ts]} for i, (a, ts) in enumerate(rows.items(), 1)]
    json.dump(draft, open(sj, "w"), ensure_ascii=False, indent=1)
    print(f"Draft of sentences in {sj}: review clip, part, sentence and takes.")
template = open(os.path.join(HERE, "../assets/choose-takes.html")).read()
FAVORITE, NOTE = html.escape(label("favorite")), html.escape(label("note"))
sections = []
cj = os.path.join(out, ".proxies.json")                 # which cut each proxy has, to redo it if it changes
cache = json.load(open(cj)) if os.path.exists(cj) else {}
for f in json.load(open(sj)):
    cards = []
    for tk in f["takes"]:
        ks = tk if isinstance(tk, list) else [tk]
        x0, x1 = T[(f["file"], ks[0])], T[(f["file"], ks[-1])]
        lab = "Take " + "+".join(map(str, ks))
        # Exact cut from cuts.py: the proxy shows the take as it enters the video
        t_in, t_out = f.get("cuts", {}).get(lab) or (max(0, x0["start"] - 0.25), x1["end"] + 0.35)
        name = f"{f['clip']}-t{'+'.join(map(str, ks))}.mp4"
        if cache.get(name) != [t_in, t_out] or not os.path.exists(os.path.join(out, name)):
            cache[name] = [t_in, t_out]
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t_in:.2f}", "-to", f"{t_out:.2f}", "-i", os.path.join(rec, f["file"]),
                            "-vf", "scale=360:-2,fps=30", "-c:v", "libx264", "-crf", "26", "-preset", "veryfast",
                            "-c:a", "aac", "-b:a", "128k", os.path.join(out, name)], check=True)
        text = " / ".join(T[(f["file"], k)]["text"] for k in ks)
        fav = lab == f.get("favorite")
        mark = f.get("chosen", f.get("favorite")) == lab
        cards.append(f'<label class="card{" fav" if fav else ""}"><video src="{name}" controls preload="metadata" playsinline></video>'
                     f'<span><input type="radio" name="c{f["clip"]}" value="{lab}" data-label="{html.escape(take_name(lab))}"{" checked" if mark else ""}> {html.escape(take_name(lab))} · {t_out - t_in:.1f} s</span>'
                     f'{f"<em>{FAVORITE}</em>" if fav else ""}<small>{html.escape(text)}</small></label>')
    part = f" {html.escape(f['part'])} ·" if f.get("part") else ""
    sections.append(f'<section data-clip="{f["clip"]}"><h2><b>{f["clip"]}</b>{part} {html.escape(f["sentence"])}</h2>'
                    + (f'<p class="reason">{FAVORITE}: {html.escape(take_name(f["favorite"]))}, {html.escape(f.get("reason", ""))}.</p>' if f.get("favorite") else "")
                    + (f'<p class="reason">{NOTE}: {html.escape(f["warning"])}.</p>' if f.get("warning") else "")
                    + f'<div class="row">{"".join(cards)}</div></section>')
json.dump(cache, open(cj, "w"))
open(os.path.join(out, "choose-takes.html"), "w").write(
    template.replace("{{TITLE}}", html.escape(title)).replace("{{SECTIONS}}", "\n".join(sections)))
print(os.path.join(out, "choose-takes.html"))
