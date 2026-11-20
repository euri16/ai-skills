#!/usr/bin/env python3
"""Finds duplicates by audio content (not by bytes or by name) among the files of one or more folders.

Usage: python3 audio-duplicates.py <folder> [<folder> ...]
Run with the python3 that has numpy (without -I, which hides the user's packages). Needs ffmpeg.
Exits 2 if a folder does not exist and 1 if the folders hold no readable audio; finding no pairs exits 0.

How it decides: trims each file's silence, compares their band spectrograms sliding the shorter one
over the longer one (so it also detects a trim of another file) and confirms similar pairs with the waveform
correlation. A pair is a duplicate if the waveform matches at 0.9 or more; a pair with the same dominant
note and an almost identical spectrum is marked as "equivalent" (for example, two 1 kHz beeps).
"""
import os, sys, itertools, shutil, subprocess

def die(msg, code=2): print(msg, file=sys.stderr); sys.exit(code)
if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"): print(__doc__.strip()); sys.exit(0)
if len(sys.argv) < 2: die(__doc__.strip())
try: import numpy as np
except ImportError: die("numpy is missing for this python3: python3 -m pip install --user numpy")
if not shutil.which("ffmpeg"): die("ffmpeg is not installed: this script needs it.")
missing = [r for r in sys.argv[1:] if not os.path.isdir(r)]
if missing: die("Folder not found: %s" % ", ".join(missing))

SR = 16000

def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         stdout=subprocess.PIPE).stdout
    x = np.frombuffer(raw, dtype=np.float32).copy()
    if len(x) == 0 or np.abs(x).max() == 0:
        return None
    a = np.abs(x); i = np.where(a > a.max() * 10 ** (-40 / 20))[0]
    return x[i[0]:i[-1] + 1]

def bands(x):
    n, h = 1024, 256
    if len(x) < n: x = np.pad(x, (0, n - len(x)))
    idx = np.arange(0, len(x) - n + 1, h)
    fr = np.stack([x[i:i + n] for i in idx]) * np.hanning(n)
    S = np.abs(np.fft.rfft(fr, axis=1)) ** 2
    e = np.unique(np.round(np.geomspace(2, S.shape[1] - 1, 33)).astype(int))
    L = 10 * np.log10(np.stack([S[:, a:b].sum(1) for a, b in zip(e[:-1], e[1:])], 1) + 1e-10)
    L = L - L.mean(1, keepdims=True)
    return L / (np.linalg.norm(L, axis=1, keepdims=True) + 1e-9)

def spec_sim(A, B):
    if len(A) > len(B): A, B = B, A
    m = len(A)
    if m < 4: return 0.0, 0.0
    best = max((A * B[o:o + m]).sum(1).mean() for o in range(len(B) - m + 1))
    return float(best), m / len(B)

def wave_corr(a, b):
    if len(a) > len(b): a, b = b, a
    b = np.concatenate([b, np.zeros(len(a))])
    n = 1 << int(np.ceil(np.log2(len(a) + len(b))))
    c = np.fft.irfft(np.fft.rfft(b, n) * np.conj(np.fft.rfft(a, n)), n)
    k = int(np.argmax(np.abs(c)[:len(b) - len(a) + 1]))
    seg = b[k:k + len(a)]
    if seg.std() == 0 or a.std() == 0: return 0.0
    return float(abs(np.corrcoef(a, seg)[0, 1]))

def tone(x):
    S = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    return np.argmax(S) * SR / len(x)

files = []
for root in sys.argv[1:]:
    for d, _, fs in os.walk(root):
        files += [os.path.join(d, f) for f in fs if f.lower().endswith((".mp3", ".wav", ".flac", ".m4a", ".ogg"))]
if not files: die("No audio files (.mp3, .wav, .flac, .m4a, .ogg) in: %s" % ", ".join(sys.argv[1:]), 1)
data = {}
for p in files:
    x = load(p)
    if x is None: print("skipped (silent or unreadable): %s" % p, file=sys.stderr)
    else: data[p] = (x, bands(x))
if not data: die("None of the %d files has audio that ffmpeg can read." % len(files), 1)
found = 0
for a, b in itertools.combinations(sorted(data), 2):
    s, cov = spec_sim(data[a][1], data[b][1])
    if s < 0.9 or cov < 0.2: continue
    w = wave_corr(data[a][0], data[b][0])
    ta, tb = tone(data[a][0]), tone(data[b][0])
    same_tone = abs(ta - tb) <= max(5, 0.01 * max(ta, tb))
    if w >= 0.9:
        kind = "DUPLICATE"
    elif same_tone and s >= 0.93:
        kind = "equivalent"
    else:
        continue
    found += 1
    print("%s  waveform %.2f  spectrum %.2f  %s  <->  %s" % (kind, w, s, a, b))
print("pairs found: %d among %d files" % (found, len(data)))
