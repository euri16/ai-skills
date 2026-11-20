#!/usr/bin/env python3
"""Check the scene timing of a visual video (a piece with no camera take) against its reading time or its voice-over.

Usage: python3 verify-scenes.py <project_dir> [--cps N]
--cps sets the reading ceiling in characters per second for the language of the piece (default 17, a conservative
value; a language read faster or slower takes its own published figure).
Reads index.html and, when the composition has <audio id="voice">, cut.json. A scene is an element with the classes
"scene" and "clip". Exit code 1 if a check fails or if there is nothing to check; 2 for wrong arguments.

Always:
- there is at least one scene, every scene has data-start, data-duration and data-visual-seconds, and all of them sit
  on the same track;
- starts and durations fall on whole frames at 30 fps, the first scene starts at 0, each scene starts where the
  previous one ends and the last one ends with the composition (data-duration of the root).

Without voice (no <audio id="voice">), what is written on screen is the script and each screen is timed by reading:
- read text is the text inside the elements with class "read" of the scene; labels outside them get a glance and
  are not counted;
- a scene needs: 0.45 s of entry (not the first scene) + its reading time, the larger of 1 s and its characters
  divided by the reading ceiling (a scene with no read text needs none, and then must declare a visual) + data-visual-seconds (the time
  its lead visual takes to act, 0 if it has none) + 0.8 s of hold on the last scene;
- it fails if a scene lasts less than that, or over 1.5 s more (a screen left up once it has been read drags);
- it fails if there is no <audio> from assets/music/ (music carries a piece without voice) or if the composition has
  subtitle clips (class "cap"): there is no speech to subtitle.

With voice (<audio id="voice" src="voice.wav">), the voice sets the timing:
- cut.json names voice.wav as its master, and the composition lasts the voice's data-start plus the cut;
- every scene declares data-word, the index (from 0, counted across all segments of cut.json) of the first word of its
  beat; the first scene is word 0 and the indexes grow;
- every scene after the first starts 0.3 s before that word (one frame of tolerance), so it has settled when the word
  is heard;
- there is at least one subtitle clip (class "cap"), and none starts before the voice or ends after the composition.
"""
import json, math, os, sys
from html.parser import HTMLParser

FPS = 30
CPS, MIN_READ = 17.0, 1.0          # default reading ceiling in characters per second (--cps) and the shortest reading time
ENTRY, CLOSE_HOLD, SLACK = 0.45, 0.8, 1.5
LEAD = 0.3                         # a voiced scene starts this long before the first word of its beat
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

args = sys.argv[1:]
if "--cps" in args:
    i = args.index("--cps")
    try:
        CPS = float(args[i + 1])
        if not CPS > 0: raise ValueError
    except (IndexError, ValueError):
        print("verify-scenes: --cps takes a number above 0 (characters per second)", file=sys.stderr)
        sys.exit(2)
    del args[i:i + 2]
if len(args) != 1 or args[0] in ("-h", "--help"):
    print(__doc__)
    sys.exit(0 if len(args) == 1 else 2)
project = args[0]


def stop(msg):
    print("FAIL", msg)
    sys.exit(1)


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.root, self.scenes, self.caps, self.audios = [], None, [], [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        if "data-composition-id" in a and self.root is None:
            self.root = a
        if tag == "audio":
            self.audios.append(a)
        if "cap" in classes and "clip" in classes:
            self.caps.append(a)
        scene = None
        if "scene" in classes and "clip" in classes:
            scene = {"attrs": a, "text": []}
            self.scenes.append(scene)
        if tag not in VOID:
            self.stack.append((tag, scene, "read" in classes))

    def handle_endtag(self, tag):
        for k in range(len(self.stack) - 1, -1, -1):
            if self.stack[k][0] == tag:
                del self.stack[k:]
                return

    def handle_data(self, data):
        if not any(read for _, _, read in self.stack):
            return
        for _, scene, _ in reversed(self.stack):
            if scene:
                scene["text"].append(data)
                return


path = os.path.join(project, "index.html")
if not os.path.exists(path):
    stop(f"index.html not found in {project}")
page = Page()
page.feed(open(path, encoding="utf-8").read())
if page.root is None or "data-duration" not in page.root:
    stop("index.html has no composition root with data-duration")
if not page.scenes:
    stop('no scene found (elements with class="scene clip"): nothing was checked')
total = float(page.root["data-duration"])
failures, rows = [], []


def on_frame(x):
    return abs(x * FPS - round(x * FPS)) < 1e-3


def number(attrs, key, label):
    try:
        return float(attrs[key])
    except (KeyError, ValueError):
        failures.append(f"{label} has no numeric {key}")
        return None


scenes = []
for k, s in enumerate(page.scenes, 1):
    a = s["attrs"]
    label = a.get("id") or f"scene {k}"
    start, dur, visual = (number(a, key, label) for key in ("data-start", "data-duration", "data-visual-seconds"))
    text = " ".join("".join(s["text"]).split())
    scenes.append({"label": label, "start": start, "dur": dur, "visual": visual, "text": text, "attrs": a})
if failures:
    for f in failures:
        print("FAIL", f)
    sys.exit(1)

if len({s["attrs"].get("data-track-index") for s in scenes}) != 1:
    failures.append("the scenes are not all on the same track (data-track-index)")
if not on_frame(total):
    failures.append(f"the composition lasts {total} s, which is not a whole number of frames at {FPS} fps")
for s in scenes:
    if not on_frame(s["start"]) or not on_frame(s["dur"]):
        failures.append(f"{s['label']}: start {s['start']} or duration {s['dur']} is not on a whole frame at {FPS} fps")
if abs(scenes[0]["start"]) > 1e-6:
    failures.append(f"{scenes[0]['label']} starts at {scenes[0]['start']} s: the first scene starts at 0, on frame 0")
for prev, s in zip(scenes, scenes[1:]):
    end = prev["start"] + prev["dur"]
    if abs(end - s["start"]) > 1e-3:
        failures.append(f"{s['label']} starts at {s['start']:.3f} s and {prev['label']} ends at {end:.3f} s: "
                        + ("they overlap" if s["start"] < end else "the screen is empty between them"))
end = scenes[-1]["start"] + scenes[-1]["dur"]
if abs(end - total) > 1e-3:
    failures.append(f"{scenes[-1]['label']} ends at {end:.3f} s and the composition at {total:.3f} s")

voice = next((a for a in page.audios if a.get("id") == "voice"), None)
music = [a for a in page.audios if (a.get("src") or "").startswith("assets/music/")]
if voice is None:
    mode = "without voice"
    if not music:
        failures.append("no <audio> from assets/music/: a visual video without voice carries music")
    if page.caps:
        failures.append(f"{len(page.caps)} subtitle clips (class \"cap\") in a composition without <audio id=\"voice\">")
    for k, s in enumerate(scenes):
        chars = len(s["text"])
        if not chars and s["visual"] <= 0:
            failures.append(f"{s['label']} has no read text (class \"read\") and no data-visual-seconds: an empty screen")
        reading = max(MIN_READ, chars / CPS) if chars else 0
        need = (ENTRY if k else 0) + reading + s["visual"] + (CLOSE_HOLD if k == len(scenes) - 1 else 0)
        low = math.ceil(need * FPS - 1e-6) / FPS
        verdict = "ok"
        if s["dur"] < low - 1e-6:
            verdict = f"short by {low - s['dur']:.2f} s"
            failures.append(f"{s['label']} lasts {s['dur']:.2f} s and needs {low:.2f} s to be read ({chars} characters)")
        elif s["dur"] > low + SLACK + 1e-6:
            verdict = f"long by {s['dur'] - low - SLACK:.2f} s"
            failures.append(f"{s['label']} lasts {s['dur']:.2f} s, over {SLACK} s more than the {low:.2f} s it needs: it drags")
        rows.append(f"{s['label']}: {len(s['text'].split())} words, {chars} characters, needs {low:.2f} s, "
                    f"lasts {s['dur']:.2f} s, {verdict}")
else:
    mode = "with voice"
    cut_path = os.path.join(project, "cut.json")
    if not os.path.exists(cut_path):
        stop("the composition has <audio id=\"voice\"> and there is no cut.json in the project (build-cut.py single --voice-only)")
    cut = json.load(open(cut_path))
    if cut.get("master") != "voice.wav" or voice.get("src") != "voice.wav":
        stop(f"the voice plays {voice.get('src')!r} and cut.json names the master {cut.get('master')!r}: both must be voice.wav")
    offset = float(voice.get("data-start", 0))
    words = [w for seg in cut["segments"] for w in seg["words"]]
    if not words:
        stop("cut.json has no words: nothing was checked")
    if abs(offset + cut["duration"] - total) > 1 / FPS + 1e-6:
        failures.append(f"the composition lasts {total:.3f} s and the voice ends at {offset + cut['duration']:.3f} s")
    last = -1
    for k, s in enumerate(scenes):
        raw = s["attrs"].get("data-word")
        if raw is None or not raw.isdigit() or int(raw) >= len(words):
            failures.append(f"{s['label']} has no valid data-word (an index from 0 to {len(words) - 1} of the words of cut.json)")
            continue
        i = int(raw)
        if i <= last or (k == 0 and i != 0):
            failures.append(f"{s['label']}: data-word {i} " + ("must be 0 on the first scene" if k == 0 else "does not come after the previous scene's"))
        last = i
        want = 0.0 if k == 0 else max(0.0, offset + words[i]["t0"] - LEAD)
        verdict = "ok"
        if abs(s["start"] - want) > 1 / FPS + 1e-6:
            verdict = f"off by {s['start'] - want:+.2f} s"
            failures.append(f"{s['label']} starts at {s['start']:.3f} s and its word \"{words[i]['w']}\" asks for {want:.3f} s "
                            f"({LEAD} s before the word at {offset + words[i]['t0']:.3f} s)")
        rows.append(f"{s['label']}: word {i} \"{words[i]['w']}\" at {offset + words[i]['t0']:.2f} s, starts at {s['start']:.2f} s, {verdict}")
    if not page.caps:
        failures.append("no subtitle clip (class \"cap\") in a composition with voice")
    for c in page.caps:
        try:
            c0, c1 = float(c["data-start"]), float(c["data-start"]) + float(c["data-duration"])
        except (KeyError, ValueError):
            failures.append(f"subtitle {c.get('id', '?')} has no numeric data-start and data-duration")
            continue
        if c0 < offset - 1e-6 or c1 > total + 1e-6:
            failures.append(f"subtitle {c.get('id', '?')} ({c0:.2f} to {c1:.2f} s) falls outside the voice ({offset:.2f} to {total:.2f} s)")

print(f"{len(scenes)} scenes, {total:.2f} s, {mode}" + (f", {len(page.caps)} subtitles" if voice is not None else ""))
for r in rows:
    print(" ", r)
for f in failures:
    print("FAIL", f)
print("OK" if not failures else f"{len(failures)} failures")
sys.exit(1 if failures else 0)
