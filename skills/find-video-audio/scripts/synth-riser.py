#!/usr/bin/env python3
"""Clean synthesized risers (air and tonal) that land on the brand motif, plus an existing reference riser.

Usage: synth-riser.py <output_dir> <hit_without_motif.wav> <reference_riser.wav> <bass_dB> --notes <note1>,<note2> [--hit-at <seconds>|auto]
<bass_dB>: gain in dB added to the motif bass. At 0 the bass peaks just under the riser (0.55 against 0.6 of full
scale); -20 leaves it about 20 dB under the riser.
--notes is required: the two notes of the workspace's brand motif in the bass register (octave 2, for example E2,A2).
--hit-at: where the hit's transient is inside its file, in seconds (default 0.20); "auto" finds it at the first
sample that reaches half of the peak. Only the hit's click is used, on each note of the motif.
Writes each riser without and with the motif, and "0 all in a row (each without and with motif).wav".
Needs numpy and ffmpeg.
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
def two_notes(opt):
    if "--notes" not in opt: die("missing --notes <note1>,<note2>: the brand motif from the workspace's brand guide")
    parts = opt["--notes"].split(",")
    if len(parts) != 2: die("--notes takes two notes separated by a comma (E2,A2), not \"%s\"" % opt["--notes"])
    return freq(parts[0].strip()), freq(parts[1].strip())
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
pos, opt = split_args(sys.argv[1:], ("--notes", "--hit-at"))
if len(pos) != 4: die(__doc__.strip())
out, hitpath, refriser, dbb = pos; GAP = 0.22; RISE = 1.2; rng = np.random.default_rng(11)
F1, F2 = two_notes(opt)
BASS = 0.55*10**(number(dbb, "<bass_dB>")/20)
def osc(ftrack, amp, drive=3.0):
    ph = 2*np.pi*np.cumsum(ftrack)/SR; return np.tanh(drive*np.sin(ph)*amp)/np.tanh(drive)
orig = load(hitpath, "Hit"); tr = click(orig, hit_instant(orig, opt, hitpath))
def bass_motif():
    T = GAP + 1.0; t = np.arange(int(T*SR))/SR
    a_env = np.exp(-t*2.0)*np.minimum(1, t/0.004)*np.clip(1-(t-GAP)/0.08, 0, 1)
    t2 = np.maximum(t-GAP, 0); b_env = np.where(t >= GAP, np.exp(-t2*3.2)*np.minimum(1, t2/0.004), 0)
    y = osc(F1*(1+1.2*np.exp(-t*45)), a_env)*0.9 + osc(np.where(t>=GAP, F2*(1+1.2*np.exp(-t2*45)), F2), b_env)
    s = int(GAP*SR); y[:len(tr)] += tr*0.5; y[s:s+len(tr)] += tr*0.7
    n = int(0.08*SR); y[-n:] *= np.linspace(1,0,n); return y
def air_riser():
    """Filtered noise whose band rises from 250 Hz to 5 kHz while the volume grows; ends dry at the landing."""
    n = int(RISE*SR); x = rng.normal(0, 1, n); N = 2048; H = 512; win = np.hanning(N); y = np.zeros(n + N)
    for i, st in enumerate(range(0, n - N, H)):
        p = st / n; fc = 250 * (5000/250) ** p; bw = 0.6 * fc
        Xf = np.fft.rfft(x[st:st+N] * win); f = np.fft.rfftfreq(N, 1/SR)
        Xf *= np.exp(-0.5 * ((f - fc) / bw) ** 2); y[st:st+N] += np.fft.irfft(Xf, N) * win
    y = y[:n]; t = np.arange(n)/SR; y *= (t/RISE) ** 2.2 * np.minimum(1, t/0.05)
    return y / np.abs(y).max()
def tonal_riser():
    """Harmonic tone that rises one octave up to the motif's first note while the filter opens; with a bit of air."""
    n = int(RISE*SR); t = np.arange(n)/SR; p = t/RISE
    f = F1/2 * 2 ** p                     # one octave below the first note up to it, arriving on the motif's first note
    ph = 2*np.pi*np.cumsum(f)/SR; y = np.zeros(n)
    for k in range(1, 24): y += np.sin(k*ph) / k * (1 / (1 + (k*f/(300 + 3500*p**2))**4))
    y = np.tanh(2.5*y); y += 0.35 * air_riser()[:n]
    y *= p ** 1.8 * np.minimum(1, t/0.05)
    return y / np.abs(y).max()
def save(p, y):
    y = np.clip(y, -1, 1); w = wave.open(p, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([y,y],1)*32767).astype("<i2").tobytes()); w.close()
os.makedirs(out, exist_ok=True)
bm = bass_motif(); seq = []
ref = load(refriser, "Reference riser"); ref /= np.abs(ref).max()
for i, (name, r) in enumerate((("reference riser", ref), ("synthetic air riser", air_riser()), ("synthetic tonal riser", tonal_riser())), 1):
    land = len(r); start = land - int(GAP*SR)
    base = np.zeros(start + len(bm) + int(0.2*SR)); base[:len(r)] += r * 0.6
    a = base * (0.9/np.abs(base).max()); save(out + "/%da %s, without motif.wav" % (i, name), a)
    b = base.copy(); b[start:start+len(bm)] += bm * BASS; b *= 0.9/np.abs(b).max(); save(out + "/%db %s, with motif.wav" % (i, name), b)
    seq += [a, np.zeros(int(0.8*SR)), b, np.zeros(int(1.4*SR))]
save(out + "/0 all in a row (each without and with motif).wav", np.concatenate(seq)); print("ok")
