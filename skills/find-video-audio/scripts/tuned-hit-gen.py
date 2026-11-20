#!/usr/bin/env python3
"""Tuned emphasis hit: the brand motif as a synthesized low bass that carries the click of an existing hit. Only the
hit's click is used (60 ms from its transient, without the lows); the hit's body is not mixed in. Two variants:
"joined" (the first note is sustained until the second, each with its click) and "single hit" (one attack, the note
glides to the second without a new hit).

Usage: tuned-hit-gen.py <output_dir> <hit.wav> <options.tsv> [--hit-at <seconds>|auto]
options.tsv: name<TAB>note1<TAB>note2 (notes such as E2, A2, F#2).
--hit-at: where the hit's transient is inside its file, in seconds (default 0.20); "auto" finds it at the first
sample that reaches half of the peak.
Writes <output_dir>/joined/ and <output_dir>/single hit/, each with one WAV per option, peak at 0.7 of full scale,
and "0 all in a row.wav". Needs numpy and ffmpeg.
"""
import sys, os, shutil, subprocess, wave
def die(msg, code=2): print(msg, file=sys.stderr); sys.exit(code)
if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"): print(__doc__.strip()); sys.exit(0)
try: import numpy as np
except ImportError: die("numpy is missing for this python3: python3 -m pip install --user numpy")
def split_args(argv, flags):
    """Separates positional arguments from the --flag value pairs, wherever they are written."""
    pos, opt, i = [], {}, 0
    while i < len(argv):
        if argv[i] in flags:
            if i + 1 >= len(argv): die("%s needs a value" % argv[i])
            opt[argv[i]] = argv[i + 1]; i += 2
        elif argv[i].startswith("--"): die("Unknown option: %s" % argv[i])
        else: pos.append(argv[i]); i += 1
    return pos, opt
def number(text, what):
    try: return float(text)
    except ValueError: die("%s must be a number, not \"%s\"" % (what, text))
SR = 48000
NAMES = {"C":0,"C#":1,"Db":1,"D":2,"D#":3,"Eb":3,"E":4,"F":5,"F#":6,"Gb":6,"G":7,"G#":8,"Ab":8,"A":9,"A#":10,"Bb":10,"B":11}
def freq(n):
    try: return 440.0 * 2 ** ((NAMES[n[:-1]] - 9 + 12 * (int(n[-1]) - 4)) / 12)
    except (KeyError, ValueError, IndexError): die("\"%s\" is not a note: write the name and the octave, such as E2, F#2 or Bb4" % n)
def load(p, what="audio", channels=1):
    if not os.path.isfile(p): die("%s not found: %s" % (what, p))
    if not shutil.which("ffmpeg"): die("ffmpeg is not installed: this script needs it.")
    x = np.frombuffer(subprocess.run(['ffmpeg','-v','quiet','-i',p,'-ac',str(channels),'-ar',str(SR),'-f','f32le','-'],stdout=subprocess.PIPE).stdout, dtype=np.float32).copy()
    if len(x) == 0 or np.abs(x).max() == 0: die("%s has no audio that ffmpeg can read: %s" % (what, p), 1)
    return x
def hit_instant(x, opt, path):
    """Seconds from the start of the hit file to its transient: --hit-at <seconds>, --hit-at auto or 0.20."""
    v = opt.get("--hit-at", "0.20")
    if v == "auto":
        t = max(0.0, int(np.argmax(np.abs(x) >= 0.5 * np.abs(x).max())) / SR - 0.002)
        print("hit transient found at %.3f s" % t)
    else:
        t = number(v, "--hit-at")
    if t < 0 or len(x) < int((t + 0.06) * SR):
        die("%s lasts %.2f s and its transient is expected at %.2f s: pass --hit-at <seconds> or --hit-at auto" % (path, len(x) / SR, t), 1)
    return t
def click(x, t):
    """The hit's click: 60 ms from its transient, without the lows, to give the synthesized bass a real attack."""
    tr = x[int(t*SR):int((t+0.06)*SR)].copy()
    X = np.fft.rfft(tr); fr = np.fft.rfftfreq(len(tr), 1/SR); X[fr < 300] *= (fr[fr < 300]/300)**2; tr = np.fft.irfft(X, len(tr))
    tr *= np.linspace(1,0,len(tr))**0.5; peak = np.abs(tr).max()
    return tr / peak if peak > 0 else tr
pos, opt = split_args(sys.argv[1:], ("--hit-at",))
if len(pos) != 3: die(__doc__.strip())
out, hitpath, optfile = pos; GAP = 0.22
def osc(ftrack, amp, drive=3.0):
    ph = 2*np.pi*np.cumsum(ftrack)/SR; y = np.sin(ph)*amp
    return np.tanh(drive*y)/np.tanh(drive)
if not os.path.isfile(optfile): die("Options file not found: %s" % optfile)
orig = load(hitpath, "Hit"); tr = click(orig, hit_instant(orig, opt, hitpath))
def tail(y, f=0.08):
    n = int(f*SR); y[-n:] *= np.linspace(1,0,n); return y
def joined(f1, f2):
    T = GAP + 1.1; t = np.arange(int(T*SR))/SR
    # first hit: sustained, fades out 80 ms after the second comes in
    a_env = np.exp(-t*2.0) * np.minimum(1, t/0.004); cut = (t - GAP)/0.08; a_env *= np.clip(1 - cut, 0, 1)
    a = osc(f1*(1+1.2*np.exp(-t*45)), a_env)
    t2 = t - GAP; b_env = np.where(t2 >= 0, np.exp(-np.maximum(t2,0)*3.2)*np.minimum(1, np.maximum(t2,0)/0.004), 0)
    b = osc(np.where(t2 >= 0, f2*(1+1.2*np.exp(-np.maximum(t2,0)*45)), f2), b_env)
    y = a*0.9 + b; s = int(GAP*SR); y[:len(tr)] += tr*0.5; y[s:s+len(tr)] += tr*0.7
    return tail(y)
def single_hit(f1, f2, glide=0.06):
    T = GAP + 1.1; t = np.arange(int(T*SR))/SR
    g = np.clip((t - GAP)/glide, 0, 1); g = g*g*(3-2*g)           # smooth 60 ms glide
    f = (f1 + (f2 - f1)*g) * (1 + 1.2*np.exp(-t*45))             # 808 drop only on the attack
    env = np.minimum(1, t/0.004) * np.where(t < GAP, np.exp(-t*1.6), np.exp(-GAP*1.6)*np.exp(-(t-GAP)*3.0))
    y = osc(f, env); y[:len(tr)] += tr*0.7
    return tail(y)
def save(p, y):
    y = np.clip(y, -1, 1); w = wave.open(p, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([y,y],1)*32767).astype("<i2").tobytes()); w.close()
def f0_of(seg):
    seg = seg - seg.mean(); c = np.correlate(seg, seg, "full")[len(seg)-1:]; lo, hi = int(SR/400), int(SR/40)
    return SR/(lo + np.argmax(c[lo:hi]))
rows = [l.rstrip("\n").split("\t") for l in open(optfile) if l.strip()]
if not rows: die("%s has no options: one per line, name<TAB>note1<TAB>note2" % optfile)
for r in rows:
    if len(r) != 3: die("%s: each line is name<TAB>note1<TAB>note2, separated by tabs; found: %s" % (optfile, " | ".join(r)))
rows = [(n, freq(a), freq(b), a, b) for n, a, b in rows]
for sub, fn in (("joined", joined), ("single hit", single_hit)):
    d = out+"/"+sub; os.makedirs(d, exist_ok=True); seq = []
    for n, fa, fb, a, b in rows:
        y = fn(fa, fb); y *= 0.7/np.abs(y).max(); save(d+"/"+n+".wav", y); seq += [y, np.zeros(int(1.0*SR))]
        g = int(GAP*SR)
        print("%-14s %-30s 1st %.0f Hz (%.0f)  2nd %.0f Hz (%.0f)" % (sub, n, f0_of(y[int(0.08*SR):g-int(0.02*SR)]), fa, f0_of(y[g+int(0.12*SR):g+int(0.6*SR)]), fb))
    save(d+"/0 all in a row.wav", np.concatenate(seq))
