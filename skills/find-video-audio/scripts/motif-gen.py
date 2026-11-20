#!/usr/bin/env python3
"""Generates two-note motif options (synthesized marimba) alone and over the emphasis hit.

Usage: motif-gen.py <output_dir> <hit.wav> <level 0-1> <options.tsv> [--hit-at <seconds>|auto]
options.tsv: name<TAB>note1<TAB>note2[<TAB>gap<TAB>ring<TAB>vel1] (notes such as C4, F#4, Ab4...;
the optional columns are the seconds between notes, the ring of the second note and the velocity of the first).
<level> is the motif peak relative to the hit peak (0.5 is 6 dB under it).
--hit-at: where the hit's transient is inside its file, in seconds (default 0.20); "auto" finds it at the first
sample that reaches half of the peak. The motif starts on that instant.
Writes <output_dir>/alone/ and <output_dir>/over the hit/, each with "0 all in a row.wav". Needs numpy and ffmpeg.
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
pos, opt = split_args(sys.argv[1:], ("--hit-at",))
if len(pos) != 4: die(__doc__.strip())
out, hitpath, optfile = pos[0], pos[1], pos[3]; LEVEL = number(pos[2], "<level>")
if not 0 < LEVEL <= 1: die("<level> goes from 0 to 1 (the motif peak relative to the hit peak), not %s" % pos[2])
if not os.path.isfile(optfile): die("Options file not found: %s" % optfile)
rng = np.random.default_rng(7)
def marimba(f, dur, vel=1.0):
    t = np.arange(int(dur * SR)) / SR
    y = (np.sin(2*np.pi*f*t)*np.exp(-t*3.8) + 0.45*np.sin(2*np.pi*3.98*f*t)*np.exp(-t*14) + 0.15*np.sin(2*np.pi*10.1*f*t)*np.exp(-t*28))
    y = (y + rng.normal(0, 1, len(t))*np.exp(-t*900)*0.25) * np.minimum(1, t/0.002)
    return y * vel
def reverb(x, rt=0.5, mix=0.18):
    n = int(rt*SR); t = np.arange(n)/SR; env = np.exp(-6.9*t/rt)
    L = rng.normal(0,1,n)*env; R = rng.normal(0,1,n)*env; L /= np.sqrt((L**2).sum()); R /= np.sqrt((R**2).sum())
    size = len(x)+n; X = np.fft.rfft(x, size)
    wl = np.fft.irfft(X*np.fft.rfft(L, size), size); wr = np.fft.irfft(X*np.fft.rfft(R, size), size)
    dry = np.zeros(size); dry[:len(x)] = x
    return np.stack([dry+mix*wl, dry+mix*wr], 1)
def motif(n1, n2, gap=0.22, ring=0.9, vel1=1.0):
    a = marimba(freq(n1), gap+0.25, vel1); fade = int(0.12*SR); a[-fade:] *= np.linspace(1,0,fade)
    b = marimba(freq(n2), ring, 1.0)
    y = np.zeros(int((gap+ring)*SR)); y[:len(a)] += a; s = int(gap*SR); y[s:s+len(b)] += b
    return y
def rms(y): return np.sqrt((y**2).mean())
def save(p, y):
    w = wave.open(p, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(y,-1,1)*32767).astype("<i2").tobytes()); w.close()
rows = [l.rstrip("\n").split("\t") for l in open(optfile) if l.strip()]
if not rows: die("%s has no options: one per line, name<TAB>note1<TAB>note2" % optfile)
for r in rows:
    if len(r) < 3: die("%s: each line is name<TAB>note1<TAB>note2[<TAB>gap<TAB>ring<TAB>vel1], separated by tabs; found: %s" % (optfile, " | ".join(r)))
    freq(r[1]); freq(r[2])
opts = [r[:3] for r in rows]; extra = {r[0]: [number(x, "gap, ring and vel1 in %s" % optfile) for x in r[3:6]] for r in rows}
os.makedirs(out+"/alone", exist_ok=True); os.makedirs(out+"/over the hit", exist_ok=True)
alone = {n: motif(a, b, *extra[n]) for n, a, b in opts}
target = np.mean([rms(y) for y in alone.values()]); alone = {k: v*(target/rms(v)) for k, v in alone.items()}
peak = max(np.abs(reverb(v)).max() for v in alone.values()); alone = {k: v*(0.7/peak) for k, v in alone.items()}
hit = load(hitpath, "Hit", channels=2).reshape(-1,2); T0 = hit_instant(hit.mean(1), opt, hitpath)
seq_alone, seq_ctx = [], []
for n, a, b in opts:
    s = reverb(alone[n]); save(out+"/alone/"+n+".wav", s); seq_alone += [s, np.zeros((int(0.9*SR),2))]
    total = int(T0*SR)+len(s)+int(0.3*SR); mix = np.zeros((total,2)); mix[:len(hit)] += hit[:total]
    layer = s*(np.abs(hit).max()*LEVEL/np.abs(s).max()); st = int(T0*SR); mix[st:st+len(layer)] += layer
    mix *= 0.95/np.abs(mix).max(); save(out+"/over the hit/"+n+".wav", mix); seq_ctx += [mix, np.zeros((int(1.0*SR),2))]
    g = int(extra[n][0]*SR) if extra[n] else int(0.22*SR); y = alone[n]
    for lab, seg, nn in (("1st", y[:g], a), ("2nd", y[g+int(0.02*SR):g+int(0.4*SR)], b)):
        Sp = np.abs(np.fft.rfft(seg*np.hanning(len(seg)))); f = np.fft.rfftfreq(len(seg),1/SR); m = (f>100)&(f<1200)
        print("%-44s %s %.0f Hz (%s = %.0f)" % (n, lab, f[np.argmax(Sp*m)], nn, freq(nn)))
ss = np.concatenate(seq_alone); save(out+"/alone/0 all in a row.wav", ss*(0.95/np.abs(ss).max()))
save(out+"/over the hit/0 all in a row.wav", np.concatenate(seq_ctx))
print("notes at %.1f dB from the hit peak" % (20*np.log10(LEVEL)))
