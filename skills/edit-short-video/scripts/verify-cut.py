#!/usr/bin/env python3
"""Measure the cut master of a piece: frozen frames, clicks at the joins, speech inside the pauses and length.

Usage: uv run -q --python 3.11 --with numpy --with silero-vad --with onnxruntime python verify-cut.py <project_dir>
(reads cut.json and the master it names: clip.mp4, or voice.wav for the voice-over of a visual video)
Exit code 1 if something fails. With voice.wav there is no image, so the frozen image check does not run and the
output says so; the other three run the same. What it measures:
- Frozen image: mean absolute difference between consecutive frames in gray at 270x480. Moving camera footage gives
  values above 1; a repeated frame gives 0, or a few ten-thousandths after another encode. Two differences in a row
  below 0.01 (three identical frames) are a frozen image.
- Click at each join: largest jump between consecutive samples in the 0.4 ms around the join divided by the median jump of
  the surrounding 20 ms. Above 2 it is heard (unless the jump is below -60 dBFS).
- Pauses: Silero VAD (analyze-video/scripts/vad.py, the same detector that marks the attempts in takes.json) must hear no
  speech inside any pause longer than 0.15 s. A breath or room noise is not speech and passes; the loudest 0.1 s of the
  pause is reported as data.
- Length: frames and audio of the master match cut.json (audio only, for voice.wav).
"""
import json, os, subprocess, sys

if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
    print(__doc__)
    sys.exit(0 if len(sys.argv) == 2 else 2)

import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../analyze-video/scripts"))
from vad import speech_prob

project = sys.argv[1]
if not os.path.exists(os.path.join(project, "cut.json")):
    sys.exit(f"verify-cut: cut.json not found in {project}")
cut = json.load(open(os.path.join(project, "cut.json")))
name = cut.get("master", "clip.mp4")
if name not in ("clip.mp4", "voice.wav"):
    sys.exit(f"verify-cut: cut.json names the master {name!r}; it must be clip.mp4 or voice.wav")
master = os.path.join(project, name)
if not os.path.exists(master):
    sys.exit(f"verify-cut: {name} not found in {project}")
voice_only = name == "voice.wav"
FPS, SR, W, H = cut["fps"], 48000, 270, 480
STILL = 0.01                         # frame difference below which two frames are the same image
failures = []


def decode_audio(rate):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", master, "-vn", "-ac", "1", "-ar", str(rate), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


# Image, decoded frame by frame as a stream; a voice-over master has none
n_frames = None
if not voice_only:
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", master, "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo", "-"],
                            stdout=subprocess.PIPE)
    prev, diffs = None, []
    while True:
        buf = proc.stdout.read(W * H)
        if len(buf) < W * H:
            break
        frame = np.frombuffer(buf, np.uint8).astype(np.int16)
        if prev is not None:
            diffs.append(np.abs(frame - prev).mean())
        prev = frame
    proc.wait()
    n_frames = len(diffs) + 1
    if n_frames != cut["frames"]:
        failures.append(f"clip.mp4 has {n_frames} frames and cut.json says {cut['frames']}")
    still = np.array(diffs) < STILL
    k = 0
    while k < len(still):
        if still[k]:
            j = k
            while j < len(still) and still[j]:
                j += 1
            if j - k >= 2:
                failures.append(f"frozen image {k / FPS:.2f}-{(j + 1) / FPS:.2f} s ({j - k + 1} identical frames)")
            k = j
        else:
            k += 1

# Audio: clicks at the joins
y = decode_audio(SR)
if not len(y):
    sys.exit(f"verify-cut: {name} has no audio that can be decoded")
if abs(len(y) / SR - cut["duration"]) > 1 / FPS:
    failures.append(f"the audio lasts {len(y) / SR:.3f} s and the cut {cut['duration']:.3f} s")
worst = 0.0
for s in cut["segments"][1:]:
    i = round(s["cut"] * SR)
    jumps = np.abs(np.diff(y[max(0, i - 480):i + 480]))
    if len(jumps) < 959:
        failures.append(f"the join before sentence {s['clip']} ({s['cut']:.3f} s) is outside the audio: not checked")
        continue
    peak = jumps[470:490].max()
    ratio = peak / (np.median(jumps) + 1e-9)
    worst = max(worst, ratio if peak > 1e-3 else 0)
    if ratio > 2 and peak > 1e-3:
        failures.append(f"click at the join before sentence {s['clip']} ({s['cut']:.3f} s): jump {ratio:.1f} times the normal one")

# Pauses: no speech, real image
y16 = decode_audio(16000)
for s in cut["segments"]:
    if s["pause"] <= 0.15:
        continue
    t0, t1 = s["end"] + 0.02, s["end"] + s["pause"] - 0.02
    t = np.arange(t0, t1, 0.032)
    prob = speech_prob(y16[round(t0 * 16000):round(t1 * 16000)].copy(), t - t0)
    level = max(10 * np.log10(np.mean(y[round(u * SR):round((u + 0.1) * SR)] ** 2) + 1e-12)
                for u in np.arange(t0, max(t0, t1 - 0.1) + 1e-9, 0.1))
    if (prob > 0.5).any():
        failures.append(f"speech inside the pause after sentence {s['clip']} at {t[np.argmax(prob > 0.5)]:.2f} s")
    print(f"pause after {s['clip']}: {s['pause']:.2f} s, Silero max {prob.max():.2f}, max level {level:.0f} dBFS")

print((f"{n_frames} frames" if not voice_only else "voice.wav: no image, frozen image check not applicable")
      + f", {len(cut['segments'])} sentences, worst jump at a join {worst:.1f}")
for f in failures:
    print("FAIL", f)
print("OK" if not failures else f"{len(failures)} failures")
sys.exit(1 if failures else 0)
