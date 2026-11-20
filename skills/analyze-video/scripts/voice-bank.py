#!/usr/bin/env python3
"""Test bench for voice_edges (vad.py): how much the voice in and out points move when the audio gets worse.

Usage: uv run -q --python 3.11 --with numpy --with silero-vad --with onnxruntime python voice-bank.py <recording_dir> <analysis_dir>
Reads <analysis_dir>/takes.json (from takes.sh). For each take with voice it computes the edges in the original audio and with four
degradations: room noise 25 dB under the voice, the take 15 dB lower with that noise, a mouth click
180 ms before the voice plus a breath from 550 to 300 ms before, and a breath from 200 to 450 ms after the voice. Prints, per degradation, the median, the p90, the
percentage of takes that move more than 50 ms and the maximum, in ms. Run it before and after changing vad.py: a
change that worsens these figures or moves the edges in the original audio does not go in.
"""
import json, os, subprocess, sys
if len(sys.argv) < 3: sys.exit(__doc__)
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vad import voice_edges, SR

rec, adir = sys.argv[1:3]
rng = np.random.default_rng(7)

def audio(f, a, b):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", f, "-vn", "-ac", "1", "-ar", str(SR),
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768

def breath(y, r0, r1, pk):
    if r0 > 0 and r1 < len(y):
        b = np.convolve(rng.standard_normal(r1 - r0).astype(np.float32), np.ones(8) / 8, "same") * np.hanning(r1 - r0)
        y[r0:r1] += b * pk * 0.12 / (np.abs(b).max() + 1e-9)

def degrade(y, cond, voice0, voice1):
    y = y.copy()
    if cond in ("noise", "low+noise"):
        if cond == "low+noise": y *= 10 ** (-15 / 20)
        r = np.cumsum(rng.standard_normal(len(y))).astype(np.float32); r -= np.convolve(r, np.ones(400) / 400, "same")
        return y + r * np.sqrt(np.mean(y ** 2)) * 10 ** (-25 / 20) / (np.sqrt(np.mean(r ** 2)) + 1e-9)
    pk = np.abs(y).max()
    if cond == "breath-after":
        breath(y, int((voice1 + 0.20) * SR), int((voice1 + 0.45) * SR), pk); return y
    c = int((voice0 - 0.18) * SR)
    if c > 50: y[c:c + 40] += (pk * 0.5 * np.hanning(40) * rng.choice([-1, 1], 40)).astype(np.float32)
    breath(y, int((voice0 - 0.55) * SR), int((voice0 - 0.30) * SR), pk)
    return y

CONDS = ("noise", "low+noise", "click+breath", "breath-after")
moves = {c: ([], []) for c in CONDS}
takes = [x for x in json.load(open(os.path.join(adir, "takes.json"))) if x["words"]]
for x in takes:
    a = max(0, x["start"] - 0.3)
    y0 = audio(os.path.join(rec, x["file"]), a, x["end"] + 0.3)
    w = x["words"]; arg = (w[0]["start"], w[-1]["end"], w[0]["end"])
    ref = voice_edges(y0, a, *arg)
    for c in CONDS:
        e, s = voice_edges(degrade(y0, c, ref[0] - a, ref[1] - a), a, *arg)
        moves[c][0].append(abs(e - ref[0]) * 1000); moves[c][1].append(abs(s - ref[1]) * 1000)
print(f"{len(takes)} takes. Movement of the edges against the original audio (ms)")
for c in CONDS:
    for lab, v in zip(("in", "out"), map(np.array, moves[c])):
        print(f"  {c:22s} {lab:7s} med {np.median(v):4.0f}  p90 {np.percentile(v, 90):4.0f}  >50ms {np.mean(v > 50) * 100:3.0f}%  max {v.max():5.0f}")
