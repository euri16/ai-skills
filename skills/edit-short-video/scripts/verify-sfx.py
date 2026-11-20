#!/usr/bin/env python3
"""Check that no sound effect masks the voice in the words it overlaps.

Usage: uv run -q --python 3.11 --with numpy python verify-sfx.py <project_dir> [--margin 6] [--cut-margin 10] [--exclude id1,id2]
Reads index.html (every <audio> with its src, data-start, data-duration and data-volume, except the voice and the music
in assets/music/, which has its own rule of about 20 dB under the voice), the voice (the master cut.json names: clip.mp4
in <video id="a-roll">, or voice.wav in <audio id="voice"> for a visual video with voice-over, placed at the data-start
of that element) and the words of cut.json, shifted by that same data-start. Exit code 1 if an effect fails, if an
<audio> lacks its timing or its file, or if there is no voice, no effect or no word to check: a check that saw nothing is
not a pass. A visual video without voice has no word to mask, so this check is not run on it.

Only the instants with real voice count, because Whisper's word times also cover the silence around each word: 10 ms
windows of the word whose voice energy is above max(word peak - 20 dB, -45 dBFS). In those windows the mean power of the
effect, with its gain, is compared with that of the voice. Every effect stays at least 6 dB under the voice there. A cut
hit between takes carries nothing synced to the word and stays at least 10 dB under it. Cut hits are the elements whose
id starts with "s-cut-" (convention of the recipes); in a composition without that convention, every sound of 0.5 s or
less that starts or ends within 50 ms of a "cut" of cut.json. What does not reach its margin is reported with the word.
"""
import argparse, html, json, os, re, subprocess, sys

SR, WIN = 48000, 480                                    # 10 ms windows

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("project")
parser.add_argument("--margin", type=float, default=6)
parser.add_argument("--cut-margin", type=float, default=10)
parser.add_argument("--exclude", default="")
args = parser.parse_args()
excluded = {x for x in args.exclude.split(",") if x}

import numpy as np


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def window_power(y):
    n = len(y) // WIN
    return (y[:n * WIN].reshape(n, WIN) ** 2).mean(axis=1)


def attributes(tag):
    return {k: html.unescape(v) for k, v in re.findall(r'([\w-]+)="([^"]*)"', tag)}


def stop(msg):
    print("FAIL", msg)
    sys.exit(1)


for name in ("index.html", "cut.json"):
    if not os.path.exists(os.path.join(args.project, name)):
        stop(f"{name} not found in {args.project}" + (": without a cut master there is no voice to check against "
             "(a visual video without voice does not run this check)" if name == "cut.json" else ""))
page = open(os.path.join(args.project, "index.html")).read()
cut = json.load(open(os.path.join(args.project, "cut.json")))
master = cut.get("master", "clip.mp4")
if master not in ("clip.mp4", "voice.wav"):
    stop(f"cut.json names the master {master!r}; it must be clip.mp4 or voice.wav")
tag, voice_id = ("audio", "voice") if master == "voice.wav" else ("video", "a-roll")
carrier = next((attributes(t) for t in re.findall(rf"<{tag}[^>]*>", page) if f'id="{voice_id}"' in t), None)
if carrier is None:
    stop(f'index.html has no <{tag} id="{voice_id}">: the voice ({master}) cannot be placed on the timeline')
if carrier.get("src") != master:
    stop(f'<{tag} id="{voice_id}"> plays {carrier.get("src")!r} and cut.json was measured on {master}')
if not os.path.exists(os.path.join(args.project, master)):
    stop(f"{master} not found in {args.project}")
offset = float(carrier.get("data-start", 0))
voice = np.r_[np.zeros(max(0, round(offset * 100))), window_power(decode(os.path.join(args.project, master)))]

# cut.json is in master time; the composition places the master at `offset`
words = [{"w": w["w"], "t0": w["t0"] + offset, "t1": w["t1"] + offset} for s in cut["segments"] for w in s["words"]]
cut_times = [s.get("cut", s["start"]) + offset for s in cut["segments"][1:]]
uses_convention = 'id="s-cut-' in page

effects = [attributes(t) for t in re.findall(r"<audio[^>]*>", page)]
effects = [e for e in effects if e.get("id") not in excluded and e.get("id") != "voice"
           and not e.get("src", "").startswith("assets/music/")]
if not effects:
    stop("no <audio> effect found in index.html: nothing was checked")
if not words:
    stop("cut.json has no words: nothing was checked")
failures, compared = [], 0
for e in effects:
    label = e.get("id") or e.get("src") or "<audio>"
    missing = [k for k in ("src", "data-start", "data-duration") if k not in e]
    if missing:
        failures.append(f"{label} has no {', '.join(missing)}")
        continue
    path = os.path.join(args.project, e["src"])
    if not os.path.exists(path):
        failures.append(f"{label}: file not found ({e['src']})")
        continue
    t0, dur, gain = float(e["data-start"]), float(e["data-duration"]), float(e.get("data-volume", 1))
    fx = window_power(decode(path)[:round(dur * SR)] * gain)
    i0 = round(t0 * 100)
    if uses_convention:
        is_cut_hit = e.get("id", "").startswith("s-cut-")
    else:
        is_cut_hit = dur <= 0.5 and any(min(abs(t0 - c), abs(t0 + dur - c)) <= 0.05 for c in cut_times)
    margin = args.cut_margin if is_cut_hit else args.margin
    for w in words:
        w0, w1 = max(w["t0"], t0), min(w["t1"], t0 + dur)
        if w1 <= w0:
            continue
        word_voice = voice[round(w["t0"] * 100):round(w["t1"] * 100)]
        if not len(word_voice):
            continue
        floor = 10 ** (max(10 * np.log10(word_voice.max() + 1e-12) - 20, -45) / 10)
        k = np.arange(round(w0 * 100), round(w1 * 100))
        k = k[(k < len(voice)) & (k - i0 >= 0) & (k - i0 < len(fx))]
        k = k[voice[k] > floor]
        if not len(k):
            continue
        compared += 1
        voice_db = 10 * np.log10(voice[k].mean() + 1e-12)
        fx_db = 10 * np.log10(fx[k - i0].mean() + 1e-12)
        if fx_db > voice_db - margin:
            failures.append(f"{label}{' (cut hit)' if is_cut_hit else ''} ({t0:.2f} s) masks \"{w['w']}\" "
                            f"({w['t0']:.2f} s): effect {fx_db:.0f} dB, voice {voice_db:.0f} dB, {voice_db - fx_db:.1f} dB under the voice")

print(f"{len(effects)} effects checked against {len(words)} words ({compared} overlaps with voice), margin {args.margin:.0f} dB "
      f"({args.cut_margin:.0f} on cut hits)")
for f in failures:
    print("FAIL", f)
print("OK" if not failures else f"{len(failures)} failures")
sys.exit(1 if failures else 0)
